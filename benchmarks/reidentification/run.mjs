import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { anonymizeText } from '../../netlify/functions/_lib/anonymize-engine.mjs'
import { adaptiveAnalyze } from '../../netlify/functions/_lib/adaptive-engine.mjs'
import { assessResidualContextRisk } from '../../netlify/functions/_lib/residual-risk.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const allTypes = ['PERSON','EMAIL','PHONE','ADDRESS','ORG','DATE','URL','CONNECTION_STRING','IP_ADDRESS','USERNAME','COORDINATE','FILE_PATH','API_KEY','CRYPTO_WALLET','ANALYTICS_ID','CREDIT_CARD','GOVERNMENT_ID','BANK_ACCOUNT','PRIVATE_KEY','COMPANY_REGISTRATION_NUMBER','INVOICE_NUMBER','EMPLOYEE_ID','BOOKING_REFERENCE','TICKET_REFERENCE','ORDER_ID','TRANSACTION_ID']

function includesLoose(text, value) {
  return text.toLowerCase().includes(String(value).toLowerCase())
}

function riskLevel(leakedExpected, residualRisky) {
  if (leakedExpected > 0) return 'critical'
  if (residualRisky >= 3) return 'high'
  if (residualRisky >= 1) return 'medium'
  return 'low'
}

async function main() {
  const fixtures = JSON.parse(await fs.readFile(path.join(__dirname, 'fixtures.json'), 'utf8'))
  const rows = []
  let critical = 0
  let highOrCritical = 0

  for (const fixture of fixtures) {
    const base = anonymizeText(fixture.input, allTypes)
    const adaptive = adaptiveAnalyze(fixture.input, base.entities, { taskDescription: fixture.task, purpose: 'ai_prompt', destination: 'external' })
    const leakedExpected = fixture.expected_absent.filter((value) => includesLoose(adaptive.adaptive_text, value))
    const residualRisky = fixture.risky_values.filter((value) => includesLoose(adaptive.adaptive_text, value))
    const allowedRetained = fixture.allowed_context.filter((value) => includesLoose(adaptive.adaptive_text, value))
    const residualContext = assessResidualContextRisk(adaptive.adaptive_text)
    const level = ['high', 'medium'].includes(residualContext.risk) && leakedExpected.length === 0 ? residualContext.risk : riskLevel(leakedExpected.length, residualRisky.length)
    if (level === 'critical') critical += 1
    if (['critical', 'high'].includes(level)) highOrCritical += 1
    rows.push({ id: fixture.id, level, leaked_expected_absent: leakedExpected, residual_risky_values: residualRisky, allowed_context_retained: allowedRetained, residual_context: residualContext })
  }

  const summary = {
    generated_at: new Date().toISOString(),
    fixtures: fixtures.length,
    critical_reidentification_failures: critical,
    high_or_critical_cases: highOrCritical,
  }
  const report = { summary, fixtures: rows }
  await fs.writeFile(path.join(__dirname, 'current-baseline.json'), JSON.stringify(report, null, 2) + '\n')
  await fs.writeFile(path.join(__dirname, 'current-baseline.md'), [
    '# Re-identification Probe Baseline',
    '',
    `Generated: ${summary.generated_at}`,
    '',
    `- Fixtures: ${summary.fixtures}`,
    `- Critical failures: ${summary.critical_reidentification_failures}`,
    `- High or critical cases: ${summary.high_or_critical_cases}`,
    '',
    ...rows.flatMap((row) => [`## ${row.id}`, '', `- Risk level: ${row.level}`, `- Leaked expected-absent values: ${row.leaked_expected_absent.join(', ') || 'none'}`, `- Residual risky values: ${row.residual_risky_values.join(', ') || 'none'}`, `- Allowed context retained: ${row.allowed_context_retained.join(', ') || 'none'}`, `- Residual context factors: ${row.residual_context.factors.map((factor) => factor.label).join(', ') || 'none'}`, '']),
  ].join('\n'))
  console.log(JSON.stringify(summary, null, 2))
  if (critical > 0) process.exitCode = 1
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
