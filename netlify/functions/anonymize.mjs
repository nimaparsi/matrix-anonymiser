import { anonymizeText, getLanguageWarning } from './_lib/anonymize-engine.mjs'
import { checkAndIncrementUsage, makeUsageKey } from './_lib/usage.mjs'
import { getClientIp, json, parseBody, parseCookies, verifyToken } from './_lib/common.mjs'

const SUPPORTED = new Set(['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL', 'IP_ADDRESS', 'USERNAME', 'COORDINATE', 'FILE_PATH', 'API_KEY', 'CREDIT_CARD', 'GOVERNMENT_ID', 'BANK_ACCOUNT', 'PRIVATE_KEY', 'COMPANY_REGISTRATION_NUMBER', 'INVOICE_NUMBER', 'BOOKING_REFERENCE', 'TICKET_REFERENCE', 'ORDER_ID', 'TRANSACTION_ID'])

export async function handler(event) {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' })

  const started = Date.now()
  const body = parseBody(event)
  if (!body) return json(400, { detail: 'Invalid JSON body' })

  const text = String(body.text || '')
  const maxChars = Number(process.env.MAX_INPUT_CHARS || 50000)
  if (!text.trim()) return json(400, { detail: 'Text is required' })
  if (text.length > maxChars) return json(413, { detail: 'Input exceeds character limit' })

  const cookies = parseCookies(event.headers.cookie || '')
  const secret = process.env.JWT_SECRET || 'dev-secret-change-me'
  const payload = cookies.pro_token ? verifyToken(cookies.pro_token, secret) : null
  const isPro = payload?.tier === 'pro'

  const usageKey = makeUsageKey(getClientIp(event), event.headers['user-agent'] || 'unknown', isPro)
  const usage = await checkAndIncrementUsage(usageKey, isPro)
  if (!usage.allowed) {
    return json(429, {
      detail: {
        code: 'USAGE_LIMIT_EXCEEDED',
        message: 'Daily limit reached',
        used: usage.used,
        limit: usage.limit,
      },
    })
  }

  const threshold = Number(process.env.BOT_CHALLENGE_THRESHOLD || 20)
  const challengeSecret = process.env.BOT_CHALLENGE_SECRET || ''
  if (usage.used > threshold && challengeSecret) {
    if ((event.headers['x-bot-challenge'] || '') !== challengeSecret) {
      return json(403, { detail: { code: 'BOT_CHALLENGE_REQUIRED', message: 'Bot challenge failed' } })
    }
  }

  const requested = Array.isArray(body.entity_types) ? body.entity_types : ['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL', 'API_KEY', 'CREDIT_CARD', 'GOVERNMENT_ID', 'BANK_ACCOUNT', 'PRIVATE_KEY', 'COMPANY_REGISTRATION_NUMBER', 'INVOICE_NUMBER', 'BOOKING_REFERENCE', 'TICKET_REFERENCE', 'ORDER_ID', 'TRANSACTION_ID', 'IP_ADDRESS', 'USERNAME', 'COORDINATE', 'FILE_PATH']
  const selected = requested.filter((x) => SUPPORTED.has(x))
  if (selected.length === 0) return json(400, { detail: 'No valid entity types selected' })

  const tagStyle = body.tag_style === 'emoji' ? 'emoji' : 'standard'
  const reversePronouns = body.reversePronouns === true || body.reverse_pronouns === true
  const language = getLanguageWarning(text)
  const out = anonymizeText(text, selected, {
    tokenStyle: tagStyle,
    reversePronouns,
  })

  return json(200, {
    anonymized_text: out.anonymized_text,
    entities: out.entities,
    counts: out.counts,
    warning: language.warning,
    cta_visaprep: out.cta_visaprep,
    meta: {
      processing_ms: Date.now() - started,
      version: 'v1-netlify',
      token_style: tagStyle,
      reverse_pronouns: reversePronouns,
      reversePronouns,
      nlp_used: false,
      usage_used: usage.used,
      usage_limit: usage.limit,
      tier: isPro ? 'pro' : 'free',
      supported_language: language.supported_language,
      detected_language: language.detected_language,
    },
  })
}
