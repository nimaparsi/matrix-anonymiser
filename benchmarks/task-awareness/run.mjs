import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { anonymizeText } from '../../netlify/functions/_lib/anonymize-engine.mjs'
import { adaptiveAnalyze } from '../../netlify/functions/_lib/adaptive-engine.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const allTypes = ['PERSON','EMAIL','PHONE','ADDRESS','ORG','DATE','URL','CONNECTION_STRING','IP_ADDRESS','USERNAME','COORDINATE','FILE_PATH','API_KEY','CRYPTO_WALLET','ANALYTICS_ID','CREDIT_CARD','GOVERNMENT_ID','BANK_ACCOUNT','PRIVATE_KEY','COMPANY_REGISTRATION_NUMBER','INVOICE_NUMBER','EMPLOYEE_ID','BOOKING_REFERENCE','TICKET_REFERENCE','ORDER_ID','TRANSACTION_ID']

function actionMatches(decisions, entityType, allowed) {
  return decisions.some((decision) => decision.entityType === entityType && allowed.includes(decision.action))
}

async function main() {
  const fixtures = JSON.parse(await fs.readFile(path.join(__dirname, 'fixtures.json'), 'utf8'))
  const results = []
  let actionExpectations = 0
  let actionMatchesTotal = 0
  let requirementExpectations = 0
  let requirementMatches = 0
  let criticalLeakage = 0

  for (const fixture of fixtures) {
    const base = anonymizeText(fixture.input, allTypes)
    const adaptive = adaptiveAnalyze(fixture.input, base.entities, {
      taskDescription: fixture.task,
      purpose: fixture.purpose,
      destination: 'external',
    })
    const actions = Object.entries(fixture.expected.actions || {})
    const matchedActions = actions.filter(([type, allowed]) => actionMatches(
      adaptive.facts.map((fact) => ({ entityType: fact.entityType, action: adaptive.decisions.find((decision) => decision.factId === fact.id)?.action })),
      type,
      allowed,
    ))
    actionExpectations += actions.length
    actionMatchesTotal += matchedActions.length
    const required = fixture.expected.required_concepts || []
    const foundRequirements = required.filter((concept) => adaptive.requirements.some((item) => item.concept === concept && item.importance === 'required'))
    requirementExpectations += required.length
    requirementMatches += foundRequirements.length
    criticalLeakage += adaptive.metrics.critical_leakage_count
    results.push({
      id: fixture.id,
      source_id: fixture.source_id,
      task: fixture.task,
      action_match: actions.length ? Number((matchedActions.length / actions.length).toFixed(3)) : 1,
      requirement_match: required.length ? Number((foundRequirements.length / required.length).toFixed(3)) : 1,
      metrics: adaptive.metrics,
      missed_actions: actions.filter(([type]) => !matchedActions.some(([matchedType]) => matchedType === type)).map(([type, allowed]) => ({ type, allowed })),
      decisions: adaptive.decisions.map((decision) => {
        const fact = adaptive.facts.find((item) => item.id === decision.factId)
        return { type: fact?.entityType, role: fact?.semanticRole, action: decision.action, relevance: decision.taskRelevance, reason: decision.reason }
      }),
    })
  }

  const summary = {
    generated_at: new Date().toISOString(),
    fixtures: fixtures.length,
    action_match_rate: actionExpectations ? Number((actionMatchesTotal / actionExpectations).toFixed(3)) : 1,
    requirement_match_rate: requirementExpectations ? Number((requirementMatches / requirementExpectations).toFixed(3)) : 1,
    critical_leakage_count: criticalLeakage,
  }
  const report = { summary, fixtures: results }
  await fs.writeFile(path.join(__dirname, 'current-baseline.json'), JSON.stringify(report, null, 2) + '\n')
  const markdown = [
    '# Task-Aware Minimum Disclosure Baseline',
    '',
    `Generated: ${summary.generated_at}`,
    '',
    `- Fixtures: ${summary.fixtures}`,
    `- Requirement match rate: ${summary.requirement_match_rate}`,
    `- Transformation action match rate: ${summary.action_match_rate}`,
    `- Critical leakage count: ${summary.critical_leakage_count}`,
    '',
    ...results.flatMap((item) => [
      `## ${item.id}`,
      '',
      `- Source: ${item.source_id}`,
      `- Task: ${item.task}`,
      `- Requirement match: ${item.requirement_match}`,
      `- Action match: ${item.action_match}`,
      `- Utility retention proxy: ${item.metrics.required_fact_retention}`,
      `- Sensitive suppression proxy: ${item.metrics.irrelevant_sensitive_suppression}`,
      item.missed_actions.length ? `- Missed actions: ${item.missed_actions.map((miss) => `${miss.type} -> ${miss.allowed.join('/')}`).join(', ')}` : '- Missed actions: none',
      '',
    ]),
  ].join('\n')
  await fs.writeFile(path.join(__dirname, 'current-baseline.md'), markdown)
  console.log(JSON.stringify(summary, null, 2))
  if (criticalLeakage > 0) process.exitCode = 1
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
