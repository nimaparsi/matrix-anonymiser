const MONEY_REGEX = /(?:£|\$|€)\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:gbp|usd|eur|pounds?|dollars?|euros?)\b/gi
const PERCENT_REGEX = /\b\d{1,3}(?:\.\d+)?%\b/g
const DURATION_REGEX = /\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(?:working\s+)?(?:day|days|week|weeks|month|months|year|years)\b/gi
const ROLE_REGEX = /\b(?:senior|lead|principal|junior|staff|head of|director of)?\s*(?:frontend|backend|full[- ]stack|software|security|data|product|design|sales|support|operations|finance|legal|clinical|nurse|doctor|engineer|manager|analyst|designer|consultant|associate|director|officer|specialist)\b/gi
const COMMERCIAL_CONFIDENTIAL_REGEX = /\b(?:acquir(?:e|ing|ed)|merger|terminate|termination|unreleased|project\s+codename|codename|price\s+increase|increase\s+prices|disciplinary|zero-day|vulnerability|contract value|salary|compensation|fundraising|cap table|debt facility)\b/gi
const LABELLED_PERSON_REGEX = /\b(?:Patient|Engineer|Founder|Candidate|Employee|Manager|Consultant|Owner|Partner|Associate|Claimant|Student|Parent contact|Customer|User)\s*:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b/g
const LABELLED_SECRET_REGEX = /\b(?:password|passwd|pwd|token|access token|client_secret|client secret|api key|secret)\s*[:=]\s*([^\s,;]{8,})/gi

const TASK_REQUIREMENT_RULES = [
  {
    concepts: ['employee_role', 'leave_duration', 'coverage_period', 'team_capacity'],
    required: /\b(staff(?:ing)?|cover(?:age)?|rota|schedule|absence|leave|handover|shift|capacity)\b/i,
    irrelevant: ['salary', 'bank_account', 'government_id', 'credential', 'personal_contact', 'home_address'],
    reason: 'Coverage planning needs role, timing, and capacity context, not direct identity or compensation details.',
  },
  {
    concepts: ['salary', 'employee_role', 'location', 'seniority'],
    required: /\b(salary|compensation|pay|market rate|competitive|benchmark|remuneration)\b/i,
    irrelevant: ['personal_contact', 'government_id', 'credential', 'home_address', 'leave_duration'],
    reason: 'Compensation review needs role and pay context but not direct contact or official identifiers.',
  },
  {
    concepts: ['error_message', 'stack_context', 'service_name', 'environment', 'request_flow'],
    required: /\b(debug|error|exception|stack trace|log|production issue|incident|root cause|failure)\b/i,
    irrelevant: ['person_name', 'email', 'phone', 'bank_account', 'government_id'],
    reason: 'Debugging needs technical context while credentials and personal identifiers should be removed.',
  },
  {
    concepts: ['obligations', 'dates', 'amounts', 'parties', 'references'],
    required: /\b(contract|agreement|obligation|clause|terms?|liability|renewal|notice|summaris[ez])\b/i,
    irrelevant: ['personal_contact', 'credential', 'bank_account'],
    reason: 'Contract review usually needs commercial obligations, dates, amounts, and party roles, not private contact data.',
  },
  {
    concepts: ['complaint_topic', 'order_or_case_reference', 'timeline', 'resolution_needed'],
    required: /\b(complaint|support|ticket|customer|case|escalation|refund|order)\b/i,
    irrelevant: ['bank_account', 'credit_card', 'credential', 'government_id', 'home_address'],
    reason: 'Support handoff needs issue context and references but should suppress payment and identity-heavy details.',
  },
  {
    concepts: ['candidate_skills', 'experience', 'role_requirements', 'availability'],
    required: /\b(candidate|recruit|interview|role requirements|hiring|applicant|cv|resume)\b/i,
    irrelevant: ['home_address', 'government_id', 'bank_account', 'credential'],
    reason: 'Recruitment screening needs capability and role fit, not official IDs or residential details.',
  },
  {
    concepts: ['amount_due', 'invoice_reference', 'payment_status', 'billing_period'],
    required: /\b(calculate|outstanding|invoice|payment|remittance|balance|amount due|reconcile)\b/i,
    irrelevant: ['person_name', 'phone', 'home_address', 'credential'],
    reason: 'Finance tasks need amounts and references while personal contact details are usually unnecessary.',
  },
  {
    concepts: ['clinical_summary', 'symptoms', 'dates', 'care_action'],
    required: /\b(patient|clinical|medical|nhs|referral|diagnosis|symptoms?|treatment|doctor|gp)\b/i,
    irrelevant: ['email', 'phone', 'home_address', 'credential'],
    reason: 'Clinical summarisation may need health facts and timing but should minimise direct identifiers.',
  },
]

const ENTITY_CONCEPTS = {
  PERSON: 'person_name',
  ORG: 'organisation_identity',
  EMAIL: 'personal_contact',
  PHONE: 'personal_contact',
  ADDRESS: 'home_address',
  DATE: 'date_or_period',
  IP_ADDRESS: 'technical_identifier',
  USERNAME: 'account_identifier',
  FILE_PATH: 'technical_identifier',
  URL: 'technical_identifier',
  API_KEY: 'credential',
  PRIVATE_KEY: 'credential',
  CONNECTION_STRING: 'credential',
  CRYPTO_WALLET: 'financial_identifier',
  CREDIT_CARD: 'credit_card',
  BANK_ACCOUNT: 'bank_account',
  GOVERNMENT_ID: 'government_id',
  COMPANY_REGISTRATION_NUMBER: 'organisation_identifier',
  EMPLOYEE_ID: 'employee_identifier',
  INVOICE_NUMBER: 'invoice_reference',
  BOOKING_REFERENCE: 'booking_reference',
  TICKET_REFERENCE: 'case_reference',
  ORDER_ID: 'order_reference',
  TRANSACTION_ID: 'transaction_reference',
  MONEY: 'amount',
  DURATION: 'duration',
  ROLE: 'role',
  PERCENTAGE: 'percentage',
  COMMERCIAL_CONFIDENTIAL: 'contextual_confidentiality',
}

function normalizeTaskText(task) {
  return String(task || '').trim().slice(0, 500)
}

export function inferTaskRequirements(taskDescription = '', purpose = 'ai_prompt') {
  const task = normalizeTaskText(taskDescription)
  const matched = TASK_REQUIREMENT_RULES.filter((rule) => rule.required.test(task))
  const base = matched.length ? matched : [{
    concepts: ['topic', 'structure', 'useful_context'],
    irrelevant: ['credential', 'government_id', 'bank_account', 'credit_card', 'personal_contact'],
    reason: 'No specific task pattern matched, so SanitiseAI applies conservative minimum-disclosure guidance.',
  }]
  const requirements = []
  const seen = new Set()
  for (const rule of base) {
    for (const concept of rule.concepts) {
      if (seen.has(concept)) continue
      seen.add(concept)
      requirements.push({ concept, importance: 'required', reason: rule.reason })
    }
    for (const concept of rule.irrelevant || []) {
      const key = `irrelevant:${concept}`
      if (seen.has(key)) continue
      seen.add(key)
      requirements.push({ concept, importance: 'irrelevant', reason: rule.reason })
    }
  }
  if (purpose === 'developer_logs' && !seen.has('credential')) {
    requirements.push({ concept: 'credential', importance: 'irrelevant', reason: 'Credentials should not be disclosed to downstream tools for debugging.' })
  }
  return requirements
}

function conceptImportance(concept, requirements) {
  const direct = requirements.find((item) => item.concept === concept)
  if (direct) return direct.importance
  if (concept === 'amount' && requirements.some((item) => item.importance === 'required' && ['salary', 'amount_due', 'amounts'].includes(item.concept))) return 'required'
  if (concept === 'role' && requirements.some((item) => item.importance === 'required' && ['employee_role', 'candidate_skills', 'role_requirements'].includes(item.concept))) return 'required'
  if (concept === 'duration' && requirements.some((item) => item.importance === 'required' && ['leave_duration', 'coverage_period'].includes(item.concept))) return 'required'
  if (concept === 'date_or_period' && requirements.some((item) => item.importance === 'required' && ['dates', 'coverage_period', 'billing_period'].includes(item.concept))) return 'useful'
  if (['credential', 'credit_card', 'bank_account', 'government_id'].includes(concept)) return 'irrelevant'
  if (['personal_contact', 'home_address'].includes(concept)) return 'irrelevant'
  return 'unknown'
}

function factCategory(type) {
  if (['API_KEY', 'PRIVATE_KEY', 'CONNECTION_STRING'].includes(type)) return 'AUTHENTICATION_SECRET'
  if (['CREDIT_CARD', 'BANK_ACCOUNT', 'CRYPTO_WALLET', 'MONEY', 'TRANSACTION_ID'].includes(type)) return 'FINANCIAL'
  if (['GOVERNMENT_ID', 'EMPLOYEE_ID'].includes(type)) return 'REGULATED_IDENTIFIER'
  if (['IP_ADDRESS', 'URL', 'FILE_PATH', 'USERNAME'].includes(type)) return 'INFRASTRUCTURE'
  if (['COMMERCIAL_CONFIDENTIAL'].includes(type)) return 'COMMERCIAL_SECRET'
  if (['ROLE', 'DURATION', 'PERCENTAGE'].includes(type)) return 'CONTEXT'
  return 'PERSONAL'
}

function factSensitivity(type, value = '') {
  if (['API_KEY', 'PRIVATE_KEY', 'CONNECTION_STRING', 'CREDIT_CARD', 'BANK_ACCOUNT', 'CRYPTO_WALLET'].includes(type)) return 'critical'
  if (['GOVERNMENT_ID', 'EMPLOYEE_ID', 'EMAIL', 'PHONE', 'ADDRESS'].includes(type)) return 'high'
  if (type === 'MONEY' && /salary|compensation|pay/i.test(value)) return 'high'
  if (['MONEY', 'COMMERCIAL_CONFIDENTIAL', 'IP_ADDRESS', 'USERNAME'].includes(type)) return 'medium'
  return 'medium'
}

function addRegexFacts(facts, text, regex, type, confidence = 0.75) {
  regex.lastIndex = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    const value = match[0]
    facts.push({
      id: `${type.toLowerCase()}-${match.index}-${match.index + value.length}`,
      value,
      entityType: type,
      semanticRole: ENTITY_CONCEPTS[type] || type.toLowerCase(),
      category: factCategory(type),
      sensitivity: factSensitivity(type, value),
      confidence,
      span: { start: match.index, end: match.index + value.length },
    })
  }
}

function addCapturedRegexFacts(facts, text, regex, type, captureIndex = 1, confidence = 0.7) {
  regex.lastIndex = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    const value = match[captureIndex]
    if (!value) continue
    const start = match.index + match[0].indexOf(value)
    facts.push({
      id: `${type.toLowerCase()}-${start}-${start + value.length}`,
      value,
      entityType: type,
      semanticRole: ENTITY_CONCEPTS[type] || type.toLowerCase(),
      category: factCategory(type),
      sensitivity: factSensitivity(type, value),
      confidence,
      span: { start, end: start + value.length },
    })
  }
}

function overlaps(a, b) {
  return a.span.start < b.span.end && b.span.start < a.span.end
}

function dedupeFacts(facts) {
  const sorted = [...facts].sort((a, b) => {
    const severity = { critical: 0, high: 1, medium: 2, low: 3 }
    return (severity[a.sensitivity] ?? 9) - (severity[b.sensitivity] ?? 9) || a.span.start - b.span.start
  })
  const accepted = []
  for (const fact of sorted) {
    if (accepted.some((item) => overlaps(item, fact))) continue
    accepted.push(fact)
  }
  return accepted.sort((a, b) => a.span.start - b.span.start)
}

export function buildSensitiveFacts(text, entities = [], requirements = []) {
  const facts = entities.map((entity, index) => {
    const value = text.slice(entity.start, entity.end)
    const semanticRole = ENTITY_CONCEPTS[entity.type] || entity.type.toLowerCase()
    const taskRelevance = conceptImportance(semanticRole, requirements)
    return {
      id: `entity-${index + 1}`,
      value,
      entityType: entity.type,
      semanticRole,
      category: entity.category?.toUpperCase?.() || factCategory(entity.type),
      sensitivity: entity.sensitivity || factSensitivity(entity.type, value),
      confidence: entity.confidence || 0.8,
      taskRelevance,
      disclosureReason: entity.disclosure_reason || `${semanticRole} is ${taskRelevance} for the requested task`,
      replacement: entity.replacement,
      span: { start: entity.start, end: entity.end },
    }
  })
  addRegexFacts(facts, text, MONEY_REGEX, 'MONEY', 0.72)
  addRegexFacts(facts, text, PERCENT_REGEX, 'PERCENTAGE', 0.68)
  addRegexFacts(facts, text, DURATION_REGEX, 'DURATION', 0.74)
  addRegexFacts(facts, text, ROLE_REGEX, 'ROLE', 0.62)
  addRegexFacts(facts, text, COMMERCIAL_CONFIDENTIAL_REGEX, 'COMMERCIAL_CONFIDENTIAL', 0.55)
  addCapturedRegexFacts(facts, text, LABELLED_PERSON_REGEX, 'PERSON', 1, 0.68)
  addCapturedRegexFacts(facts, text, LABELLED_SECRET_REGEX, 'API_KEY', 1, 0.72)
  return dedupeFacts(facts).map((fact) => ({
    ...fact,
    taskRelevance: fact.taskRelevance || conceptImportance(fact.semanticRole, requirements),
  }))
}

function generaliseMoney(value) {
  const number = Number(String(value).replace(/[^0-9.]/g, ''))
  if (!Number.isFinite(number) || number <= 0) return '[Generalised amount]'
  const symbol = String(value).trim().startsWith('$') ? '$' : String(value).trim().startsWith('€') ? '€' : '£'
  if (number >= 1000000) return `${symbol}${Math.round(number / 100000) / 10}m approx.`
  if (number >= 1000) return `approximately ${symbol}${Math.round(number / 1000) * 1000}`
  return `approximately ${symbol}${Math.round(number / 10) * 10}`
}

function generaliseDate(value) {
  const text = String(value)
  const monthYear = text.match(/\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b/i)
  if (monthYear) return monthYear[0]
  const named = text.match(/\b\d{1,2}\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})\b/i)
  if (named) return `${named[1]} ${named[2]}`
  return '[Generalised date]'
}

function roleSubstitute(text, fact) {
  const window = text.slice(Math.max(0, fact.span.start - 120), Math.min(text.length, fact.span.end + 160))
  const role = window.match(ROLE_REGEX)
  ROLE_REGEX.lastIndex = 0
  if (role?.[0]) return `the ${role[0].trim().toLowerCase()}`
  return '[Person 1]'
}

export function planTransformation(fact, { taskDescription = '', purpose = 'ai_prompt', destination = 'external' } = {}) {
  const relevance = fact.taskRelevance || 'unknown'
  const sensitivity = fact.sensitivity || 'medium'
  if (['API_KEY', 'PRIVATE_KEY', 'CONNECTION_STRING'].includes(fact.entityType)) {
    return { action: 'block', replacement: '[Blocked secret]', taskRelevance: 'irrelevant', sensitivity, reason: 'Credentials should not be sent to downstream AI tools.' }
  }
  if (['CREDIT_CARD', 'BANK_ACCOUNT', 'CRYPTO_WALLET', 'GOVERNMENT_ID'].includes(fact.entityType)) {
    return { action: 'placeholder', replacement: fact.replacement || `[${fact.entityType} 1]`, taskRelevance: relevance, sensitivity, reason: 'High-risk identifiers are replaced by default.' }
  }
  if (fact.entityType === 'MONEY') {
    if (relevance === 'required' || /salary|compensation|amount|invoice|payment|calculate|outstanding/i.test(taskDescription)) {
      return { action: 'generalise', replacement: generaliseMoney(fact.value), taskRelevance: relevance, sensitivity, reason: 'The task may need amount context, but exact precision is reduced.' }
    }
    return { action: 'remove', replacement: '[Removed amount]', taskRelevance: 'irrelevant', sensitivity, reason: 'The amount appears unnecessary for the requested task.' }
  }
  if (fact.entityType === 'DATE') {
    if (relevance === 'required' || relevance === 'useful') {
      return { action: 'generalise', replacement: generaliseDate(fact.value), taskRelevance: relevance, sensitivity, reason: 'Date context may be useful, so exact date is reduced where possible.' }
    }
    return { action: 'placeholder', replacement: fact.replacement || '[Date 1]', taskRelevance: relevance, sensitivity, reason: 'Exact date is not clearly required.' }
  }
  if (fact.entityType === 'PERSON') {
    if (/staff|cover|absence|role|candidate|interview/i.test(taskDescription)) {
      return { action: 'role_substitute', replacement: null, taskRelevance: relevance, sensitivity, reason: 'Identity is not required; nearby role context is more useful.' }
    }
    return { action: 'placeholder', replacement: fact.replacement || '[Person 1]', taskRelevance: relevance, sensitivity, reason: 'Direct identity is usually unnecessary for downstream AI tasks.' }
  }
  if (fact.entityType === 'ROLE' || fact.entityType === 'DURATION') {
    return { action: 'allow', replacement: fact.value, taskRelevance: relevance, sensitivity, reason: 'This contextual fact appears useful for the task and is lower disclosure than identity.' }
  }
  if (relevance === 'irrelevant' && ['high', 'critical'].includes(sensitivity)) {
    return { action: 'remove', replacement: `[Removed ${fact.semanticRole.replace(/_/g, ' ')}]`, taskRelevance: relevance, sensitivity, reason: 'Sensitive fact appears unnecessary for the requested task.' }
  }
  return { action: 'placeholder', replacement: fact.replacement || `[${fact.entityType} 1]`, taskRelevance: relevance, sensitivity, reason: 'Default minimum-disclosure placeholder transformation.' }
}

export function applyAdaptiveTransformations(text, facts, decisions) {
  const decisionById = new Map(decisions.map((decision) => [decision.factId, decision]))
  let output = text
  for (const fact of [...facts].sort((a, b) => b.span.start - a.span.start)) {
    const decision = decisionById.get(fact.id)
    if (!decision || decision.action === 'allow') continue
    const replacement = decision.action === 'role_substitute' ? roleSubstitute(text, fact) : decision.replacement
    output = `${output.slice(0, fact.span.start)}${replacement}${output.slice(fact.span.end)}`
  }
  return output
}

export function adaptiveAnalyze(text, entities = [], { taskDescription = '', purpose = 'ai_prompt', destination = 'external' } = {}) {
  const requirements = inferTaskRequirements(taskDescription, purpose)
  const facts = buildSensitiveFacts(text, entities, requirements)
  const decisions = facts.map((fact) => ({ factId: fact.id, ...planTransformation(fact, { taskDescription, purpose, destination }) }))
  const adaptive_text = applyAdaptiveTransformations(text, facts, decisions)
  const leakedCritical = decisions.filter((decision) => decision.sensitivity === 'critical' && decision.action === 'allow').length
  const retainedRequired = decisions.filter((decision) => ['required', 'useful'].includes(decision.taskRelevance) && decision.action !== 'remove' && decision.action !== 'block').length
  const requiredTotal = decisions.filter((decision) => ['required', 'useful'].includes(decision.taskRelevance)).length
  const suppressedIrrelevant = decisions.filter((decision) => decision.taskRelevance === 'irrelevant' && decision.action !== 'allow').length
  const irrelevantTotal = decisions.filter((decision) => decision.taskRelevance === 'irrelevant').length
  return {
    mode: 'research_preview',
    methodology_version: 'adaptive-v1-deterministic',
    task: normalizeTaskText(taskDescription),
    purpose,
    destination,
    requirements,
    facts,
    decisions,
    adaptive_text,
    metrics: {
      required_fact_retention: requiredTotal ? Number((retainedRequired / requiredTotal).toFixed(3)) : 1,
      irrelevant_sensitive_suppression: irrelevantTotal ? Number((suppressedIrrelevant / irrelevantTotal).toFixed(3)) : 1,
      critical_leakage_count: leakedCritical,
    },
  }
}
