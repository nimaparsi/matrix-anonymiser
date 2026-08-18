import test from 'node:test'
import assert from 'node:assert/strict'
import { adaptiveAnalyze, inferTaskRequirements } from '../netlify/functions/_lib/adaptive-engine.mjs'
import { anonymizeText } from '../netlify/functions/_lib/anonymize-engine.mjs'

const allTypes = ['PERSON','EMAIL','PHONE','ADDRESS','ORG','DATE','URL','CONNECTION_STRING','IP_ADDRESS','USERNAME','FILE_PATH','API_KEY','CREDIT_CARD','GOVERNMENT_ID','BANK_ACCOUNT','PRIVATE_KEY','COMPANY_REGISTRATION_NUMBER','INVOICE_NUMBER','EMPLOYEE_ID','BOOKING_REFERENCE','TICKET_REFERENCE','ORDER_ID','TRANSACTION_ID']

test('infers task requirements from a staffing request', () => {
  const requirements = inferTaskRequirements('Create a staffing plan while this employee is away.', 'ai_prompt')
  assert.ok(requirements.some((item) => item.concept === 'employee_role' && item.importance === 'required'))
  assert.ok(requirements.some((item) => item.concept === 'salary' && item.importance === 'irrelevant'))
})

test('keeps useful task facts while suppressing irrelevant sensitive values', () => {
  const input = 'Nima Parsi is a Senior Frontend Engineer. His salary is £90,000. He will be away for eight working days. Email nima@example.com.'
  const base = anonymizeText(input, allTypes)
  const adaptive = adaptiveAnalyze(input, base.entities, { taskDescription: 'Create a staffing plan while this employee is away.', purpose: 'ai_prompt' })
  assert.equal(adaptive.metrics.critical_leakage_count, 0)
  assert.ok(adaptive.decisions.some((decision) => decision.action === 'remove'))
  assert.match(adaptive.adaptive_text, /Senior Frontend Engineer|eight working days/i)
  assert.doesNotMatch(adaptive.adaptive_text, /nima@example\.com/i)
})

test('blocks downstream disclosure of credentials', () => {
  const input = 'Debug login failure. Password TempPass-2026! token ghp_7YxvExampleSecretValue123 host 203.0.113.42.'
  const base = anonymizeText(input, allTypes)
  const adaptive = adaptiveAnalyze(input, base.entities, { taskDescription: 'Debug the authentication error.', purpose: 'developer_logs' })
  assert.ok(adaptive.decisions.some((decision) => decision.action === 'block'))
  assert.doesNotMatch(adaptive.adaptive_text, /ghp_7YxvExampleSecretValue123/i)
})
