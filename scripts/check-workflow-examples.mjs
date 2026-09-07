import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'
import { anonymizeText } from '../netlify/functions/_lib/anonymize-engine.mjs'
const examples = JSON.parse(readFileSync(new URL('../frontend/src/lib/workflowExamples.json', import.meta.url)))
for (const [slug, example] of Object.entries(examples)) {
  const result = anonymizeText(example.input, ['PERSON', 'ORG', 'EMAIL', 'PHONE', 'DATE', 'ADDRESS', 'IP_ADDRESS', 'API_KEY', 'PRIVATE_KEY', 'CREDIT_CARD', 'BANK_ACCOUNT', 'CRYPTO_WALLET', 'GOVERNMENT_ID', 'INVOICE_NUMBER', 'USERNAME'])
  const readable = result.anonymized_text.replace(/\[API Key (\d+)\]/g, '[Secret $1]')
  assert.equal(readable, example.output, slug)
  console.log(`PASS ${slug}`)
}
