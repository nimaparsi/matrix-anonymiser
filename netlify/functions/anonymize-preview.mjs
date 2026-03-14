import { anonymizeText } from './_lib/anonymize-engine.mjs'
import { json, parseBody } from './_lib/common.mjs'

const SUPPORTED = new Set([
  'PERSON',
  'EMAIL',
  'PHONE',
  'ADDRESS',
  'ORG',
  'DATE',
  'URL',
  'IP_ADDRESS',
  'USERNAME',
  'COORDINATE',
  'FILE_PATH',
  'API_KEY',
  'CREDIT_CARD',
  'GOVERNMENT_ID',
  'BANK_ACCOUNT',
  'PRIVATE_KEY',
  'COMPANY_REGISTRATION_NUMBER',
  'INVOICE_NUMBER',
  'BOOKING_REFERENCE',
  'TICKET_REFERENCE',
  'ORDER_ID',
  'TRANSACTION_ID',
])

function sumCounts(counts = {}) {
  return Object.values(counts).reduce((total, value) => total + Number(value || 0), 0)
}

export async function handler(event) {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' })

  const started = Date.now()
  const body = parseBody(event)
  if (!body) return json(400, { detail: 'Invalid JSON body' })

  const text = String(body.text || '')
  if (!text.trim()) return json(200, { counts: {}, total: 0, meta: { processing_ms: 0, version: 'v1-netlify-preview' } })

  const maxChars = Number(process.env.MAX_INPUT_CHARS || 50000)
  if (text.length > maxChars) return json(413, { detail: 'Input exceeds character limit' })

  const requested = Array.isArray(body.entity_types)
    ? body.entity_types
    : [
      'PERSON',
      'EMAIL',
      'PHONE',
      'ADDRESS',
      'ORG',
      'DATE',
      'URL',
      'API_KEY',
      'CREDIT_CARD',
      'GOVERNMENT_ID',
      'BANK_ACCOUNT',
      'PRIVATE_KEY',
      'COMPANY_REGISTRATION_NUMBER',
      'INVOICE_NUMBER',
      'BOOKING_REFERENCE',
      'TICKET_REFERENCE',
      'ORDER_ID',
      'TRANSACTION_ID',
      'IP_ADDRESS',
      'USERNAME',
      'COORDINATE',
      'FILE_PATH',
    ]

  const selected = requested.filter((type) => SUPPORTED.has(type))
  if (selected.length === 0) return json(400, { detail: 'No valid entity types selected' })

  const output = anonymizeText(text, selected, {
    tokenStyle: 'standard',
    reversePronouns: false,
  })
  const counts = output?.counts || {}

  return json(200, {
    counts,
    total: sumCounts(counts),
    meta: {
      processing_ms: Date.now() - started,
      version: 'v1-netlify-preview',
    },
  })
}
