import fs from 'node:fs/promises'
import path from 'node:path'
import { performance } from 'node:perf_hooks'
import { fileURLToPath } from 'node:url'
import { anonymizeText } from '../netlify/functions/_lib/anonymize-engine.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixturesDir = path.join(__dirname, 'fixtures')
const reportsDir = path.join(__dirname, 'reports')
const allTypes = [
  'PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL', 'CONNECTION_STRING', 'IP_ADDRESS', 'USERNAME',
  'COORDINATE', 'FILE_PATH', 'API_KEY', 'CRYPTO_WALLET', 'ANALYTICS_ID', 'CREDIT_CARD', 'GOVERNMENT_ID',
  'BANK_ACCOUNT', 'PRIVATE_KEY', 'COMPANY_REGISTRATION_NUMBER', 'INVOICE_NUMBER', 'EMPLOYEE_ID', 'BOOKING_REFERENCE',
  'TICKET_REFERENCE', 'ORDER_ID', 'TRANSACTION_ID',
]

function normalize(value) {
  return String(value).toLowerCase().replace(/\s+/g, ' ').replace(/[<>()[\]"'`]/g, '').trim()
}

function detectedOriginals(text, entities) {
  return entities.map((entity) => ({
    ...entity,
    original: text.slice(entity.start, entity.end),
    normalized: normalize(text.slice(entity.start, entity.end)),
  }))
}

function expectedMatched(expected, detections) {
  const wanted = normalize(expected.text)
  return detections.some((det) => det.type === expected.type && (det.normalized === wanted || det.normalized.includes(wanted) || wanted.includes(det.normalized)))
}

async function main() {
  await fs.mkdir(reportsDir, { recursive: true })
  const files = (await fs.readdir(fixturesDir)).filter((name) => name.endsWith('.json')).sort()
  const fixtureResults = []
  let expectedTotal = 0
  let matchedTotal = 0
  let detectedTotal = 0
  let criticalMisses = []
  let totalMs = 0

  for (const file of files) {
    const fixture = JSON.parse(await fs.readFile(path.join(fixturesDir, file), 'utf8'))
    const started = performance.now()
    const result = anonymizeText(fixture.text, allTypes)
    const elapsedMs = performance.now() - started
    const detections = detectedOriginals(fixture.text, result.entities || [])
    const expected = fixture.expected || []
    const matched = expected.filter((item) => expectedMatched(item, detections))
    const misses = expected.filter((item) => !expectedMatched(item, detections))
    const criticalTypes = new Set(fixture.critical_types || [])
    const critical = misses.filter((item) => criticalTypes.has(item.type))
    expectedTotal += expected.length
    matchedTotal += matched.length
    detectedTotal += detections.length
    totalMs += elapsedMs
    criticalMisses.push(...critical.map((item) => ({ fixture: fixture.id, ...item })))
    fixtureResults.push({
      id: fixture.id,
      domain: fixture.domain,
      elapsed_ms: Number(elapsedMs.toFixed(2)),
      expected: expected.length,
      matched: matched.length,
      missed: misses.length,
      detected: detections.length,
      recall: expected.length ? Number((matched.length / expected.length).toFixed(3)) : 1,
      misses,
      critical_misses: critical,
      counts: result.counts,
      analysis_summary: result.analysis?.summary,
    })
  }

  const recall = expectedTotal ? matchedTotal / expectedTotal : 1
  const precisionProxy = detectedTotal ? Math.min(1, matchedTotal / detectedTotal) : 1
  const f1Proxy = precisionProxy + recall ? (2 * precisionProxy * recall) / (precisionProxy + recall) : 0
  const summary = {
    generated_at: new Date().toISOString(),
    fixtures: files.length,
    expected_entities: expectedTotal,
    matched_entities: matchedTotal,
    detected_entities: detectedTotal,
    recall: Number(recall.toFixed(3)),
    precision_proxy: Number(precisionProxy.toFixed(3)),
    f1_proxy: Number(f1Proxy.toFixed(3)),
    critical_misses: criticalMisses,
    average_latency_ms: Number((totalMs / Math.max(1, files.length)).toFixed(2)),
  }
  const report = { summary, fixtures: fixtureResults }
  await fs.writeFile(path.join(reportsDir, 'current-baseline.json'), JSON.stringify(report, null, 2) + '\n')

  const md = [
    '# SanitiseAI Anonymisation Baseline',
    '',
    `Generated: ${summary.generated_at}`,
    '',
    '## Summary',
    '',
    `- Fixtures: ${summary.fixtures}`,
    `- Expected entities: ${summary.expected_entities}`,
    `- Matched expected entities: ${summary.matched_entities}`,
    `- Detected entities: ${summary.detected_entities}`,
    `- Recall: ${summary.recall}`,
    `- Precision proxy: ${summary.precision_proxy}`,
    `- F1 proxy: ${summary.f1_proxy}`,
    `- Average latency: ${summary.average_latency_ms}ms`,
    `- Critical misses: ${summary.critical_misses.length}`,
    '',
    '## Fixture Results',
    '',
    ...fixtureResults.flatMap((item) => [
      `### ${item.id}`,
      '',
      `- Domain: ${item.domain}`,
      `- Recall: ${item.recall}`,
      `- Matched: ${item.matched}/${item.expected}`,
      `- Detected: ${item.detected}`,
      `- Latency: ${item.elapsed_ms}ms`,
      item.misses.length ? `- Misses: ${item.misses.map((miss) => `${miss.type}(${miss.text})`).join(', ')}` : '- Misses: none',
      item.critical_misses.length ? `- Critical misses: ${item.critical_misses.map((miss) => `${miss.type}(${miss.text})`).join(', ')}` : '- Critical misses: none',
      '',
    ]),
  ].join('\n')
  await fs.writeFile(path.join(reportsDir, 'current-baseline.md'), md)
  console.log(JSON.stringify(summary, null, 2))
  if (criticalMisses.length > 0) process.exitCode = 1
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
