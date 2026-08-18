import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { anonymizeText } from '../../netlify/functions/_lib/anonymize-engine.mjs'
import { adaptiveAnalyze } from '../../netlify/functions/_lib/adaptive-engine.mjs'
import { assessResidualContextRisk } from '../../netlify/functions/_lib/residual-risk.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const allTypes = ['PERSON','EMAIL','PHONE','ADDRESS','ORG','DATE','URL','CONNECTION_STRING','IP_ADDRESS','USERNAME','COORDINATE','FILE_PATH','API_KEY','CRYPTO_WALLET','ANALYTICS_ID','CREDIT_CARD','GOVERNMENT_ID','BANK_ACCOUNT','PRIVATE_KEY','COMPANY_REGISTRATION_NUMBER','INVOICE_NUMBER','EMPLOYEE_ID','BOOKING_REFERENCE','TICKET_REFERENCE','ORDER_ID','TRANSACTION_ID']

function includesAny(text, pattern) {
  return new RegExp(pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(text)
}

function scoreOutput(text, fixture) {
  const requiredRetained = fixture.required_patterns.filter((pattern) => includesAny(text, pattern)).length
  const sensitiveLeaked = fixture.sensitive_patterns.filter((pattern) => includesAny(text, pattern))
  const criticalLeaked = fixture.critical_patterns.filter((pattern) => includesAny(text, pattern))
  return {
    required_facts_retained: requiredRetained,
    required_facts_total: fixture.required_patterns.length,
    task_utility: fixture.required_patterns.length ? Number((requiredRetained / fixture.required_patterns.length).toFixed(3)) : 1,
    sensitive_facts_leaked: sensitiveLeaked,
    critical_facts_leaked: criticalLeaked,
    residual_context: assessResidualContextRisk(text),
  }
}

async function main() {
  const fixtures = JSON.parse(await fs.readFile(path.join(__dirname, 'fixtures.json'), 'utf8'))
  const rows = []
  const totals = {
    original_utility: 0,
    standard_utility: 0,
    adaptive_utility: 0,
    original_sensitive_leaks: 0,
    standard_sensitive_leaks: 0,
    adaptive_sensitive_leaks: 0,
    original_critical_leaks: 0,
    standard_critical_leaks: 0,
    adaptive_critical_leaks: 0,
  }

  for (const fixture of fixtures) {
    const standard = anonymizeText(fixture.input, allTypes)
    const adaptive = adaptiveAnalyze(fixture.input, standard.entities, { taskDescription: fixture.task, purpose: fixture.purpose, destination: 'external' })
    const scores = {
      original: scoreOutput(fixture.input, fixture),
      standard: scoreOutput(standard.anonymized_text, fixture),
      adaptive: scoreOutput(adaptive.adaptive_text, fixture),
    }
    totals.original_utility += scores.original.task_utility
    totals.standard_utility += scores.standard.task_utility
    totals.adaptive_utility += scores.adaptive.task_utility
    totals.original_sensitive_leaks += scores.original.sensitive_facts_leaked.length
    totals.standard_sensitive_leaks += scores.standard.sensitive_facts_leaked.length
    totals.adaptive_sensitive_leaks += scores.adaptive.sensitive_facts_leaked.length
    totals.original_critical_leaks += scores.original.critical_facts_leaked.length
    totals.standard_critical_leaks += scores.standard.critical_facts_leaked.length
    totals.adaptive_critical_leaks += scores.adaptive.critical_facts_leaked.length
    rows.push({ id: fixture.id, task: fixture.task, scores })
  }

  const count = fixtures.length || 1
  const summary = {
    generated_at: new Date().toISOString(),
    fixtures: fixtures.length,
    average_task_utility: {
      original: Number((totals.original_utility / count).toFixed(3)),
      standard: Number((totals.standard_utility / count).toFixed(3)),
      adaptive: Number((totals.adaptive_utility / count).toFixed(3)),
    },
    sensitive_leaks: {
      original: totals.original_sensitive_leaks,
      standard: totals.standard_sensitive_leaks,
      adaptive: totals.adaptive_sensitive_leaks,
    },
    critical_leaks: {
      original: totals.original_critical_leaks,
      standard: totals.standard_critical_leaks,
      adaptive: totals.adaptive_critical_leaks,
    },
  }
  const report = { summary, fixtures: rows }
  await fs.writeFile(path.join(__dirname, 'current-baseline.json'), JSON.stringify(report, null, 2) + '\n')
  await fs.writeFile(path.join(__dirname, 'current-baseline.md'), [
    '# Privacy-Utility Comparison',
    '',
    `Generated: ${summary.generated_at}`,
    '',
    `- Fixtures: ${summary.fixtures}`,
    `- Average utility: original ${summary.average_task_utility.original}, standard ${summary.average_task_utility.standard}, adaptive ${summary.average_task_utility.adaptive}`,
    `- Sensitive leaks: original ${summary.sensitive_leaks.original}, standard ${summary.sensitive_leaks.standard}, adaptive ${summary.sensitive_leaks.adaptive}`,
    `- Critical leaks: original ${summary.critical_leaks.original}, standard ${summary.critical_leaks.standard}, adaptive ${summary.critical_leaks.adaptive}`,
    '',
    ...rows.flatMap((row) => [`## ${row.id}`, '', `- Task: ${row.task}`, `- Original utility/leaks: ${row.scores.original.task_utility} / ${row.scores.original.sensitive_facts_leaked.length}`, `- Standard utility/leaks: ${row.scores.standard.task_utility} / ${row.scores.standard.sensitive_facts_leaked.length}`, `- Adaptive utility/leaks: ${row.scores.adaptive.task_utility} / ${row.scores.adaptive.sensitive_facts_leaked.length}`, `- Adaptive residual context risk: ${row.scores.adaptive.residual_context.risk}`, '']),
  ].join('\n'))
  console.log(JSON.stringify(summary, null, 2))
  if (summary.critical_leaks.adaptive > 0) process.exitCode = 1
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
