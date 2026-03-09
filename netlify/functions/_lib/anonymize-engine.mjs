const SUPPORTED = new Set(['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL', 'IP_ADDRESS', 'USERNAME', 'COORDINATE', 'FILE_PATH', 'API_KEY', 'CREDIT_CARD', 'GOVERNMENT_ID', 'BANK_ACCOUNT', 'PRIVATE_KEY'])
const PERSON_STOPWORDS = new Set([
  'The', 'A', 'An', 'And', 'But', 'Or', 'If', 'For', 'In', 'On', 'At', 'By', 'From', 'To', 'Of', 'With',
  'No', 'Yes', 'Every', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
  'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
  'Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'UK', 'UKVI', 'Home', 'Office', 'Visa', 'City', 'Street', 'Road', 'Square', 'Place', 'Via',
  'He', 'She', 'They', 'Them', 'His', 'Her', 'Hers', 'Their', 'Theirs', 'We', 'I', 'You', 'It', 'Its', 'Our', 'Ours',
  'Time', 'Person', 'Email', 'Phone', 'Address', 'Organisation', 'Organization', 'Date', 'URL', 'Website', 'Web'
].map((x) => x.toLowerCase()))
const PERSON_CONTEXT_VERBS = new Set([
  'emailed', 'called', 'met', 'contacted', 'messaged', 'spoke',
])
const PERSON_SUBJECT_VERBS = new Set([
  'is', 'was', 'has', 'had', 'works', 'worked', 'lives', 'lived', 'moved', 'joined', 'arrived', 'said', 'wrote',
])
const PERSON_REL_WORDS = new Set(['son', 'daughter', 'colleague', 'manager', 'supervisor', 'friend'])
const STREET_SUFFIXES = new Set(['road', 'lane', 'street', 'terrace', 'view', 'avenue', 'drive', 'close', 'way', 'court', 'square', 'place', 'plaza', 'boulevard', 'sq', 'pl', 'blvd'])
const STREET_PREFIX_WORDS = new Set(['via'])
const TECH_BLOCK_WORDS = new Set([
  'ai', 'ml', 'llm', 'genai', 'api',
  'data', 'cloud', 'security', 'platform', 'service', 'services', 'system', 'systems',
  'machine', 'learning', 'healthcare', 'financial', 'exfiltration', 'detection', 'response', 'prevention',
  'briefing', 'book',
])
const CTA_ACTION_WORDS = new Set([
  'open', 'view', 'read', 'copy', 'download', 'upload', 'submit', 'click', 'start', 'continue', 'try',
])
const ORG_HINT_WORDS = new Set([
  'lab', 'labs', 'research', 'initiative', 'alliance', 'group', 'institute', 'network',
  'foundation', 'university', 'bank', 'council', 'office', 'agency', 'department',
  'school', 'faculty', 'consulting', 'analytics', 'systems', 'instituto',
  'energy', 'urban', 'coastal', 'ecologic', 'future', 'horizon', 'growth',
  'teams', 'drive', 'jira', 'salesforce', 'nightfall', 'atlassian', 'microsoft', 'google', 'visaprep',
])
const ORG_SUFFIX_WORDS = new Set([
  'ltd', 'limited', 'inc', 'llc', 'consulting', 'initiative', 'university', 'lab', 'labs',
  'research', 'alliance', 'group', 'institute', 'network', 'foundation', 'agency',
  'council', 'bank', 'office', 'department', 'school', 'faculty', 'systems', 'analytics', 'instituto',
])
const ORG_PREFIX_WORDS = new Set(['department', 'institute', 'school', 'faculty'])
const IGNORED_ENTITY_PREFIXES = [
  ['department', 'of'],
  ['school', 'of'],
  ['institute', 'of'],
  ['faculty', 'of'],
  ['centre', 'for'],
  ['center', 'for'],
]
const ORG_CONTEXT_WORDS = new Set([
  'at', 'in', 'from', 'via', 'with',
  'for', 'into', 'joined', 'joining',
  'works', 'worked', 'working',
  'employed', 'employment',
  'company', 'organisation', 'organization',
])
const FIELD_LABEL_WORDS = new Set(['person', 'email', 'phone', 'address', 'organisation', 'organization', 'date', 'url', 'website', 'web', 'ip', 'username', 'handle', 'coordinate', 'coordinates', 'path', 'filepath', 'slack', 'github'])
const DISCOURSE_WORDS = new Set(['later', 'then', 'next', 'afterward', 'afterwards', 'meanwhile'])
const COMMON_CITY_WORDS = new Set([
  'london', 'manchester', 'birmingham', 'leeds', 'liverpool', 'bristol', 'sheffield',
  'cambridge', 'oxford', 'brighton', 'new', 'york', 'paris', 'berlin', 'tokyo',
])
const NON_PERSON_SINGLE_BLOCK = new Set([
  'apple', 'google', 'microsoft', 'openai', 'amazon', 'meta',
  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
])
const NON_PERSON_NAME_WORDS = new Set([
  'coordination', 'meeting', 'review', 'infrastructure', 'climate',
  'urgent', 'subject', 'relevant', 'resources', 'internal', 'shared',
  'server', 'systems', 'data', 'strategy', 'director', 'united', 'kingdom',
  'financial', 'centre', 'center', 'tower', 'building',
  'hi', 'hello', 'dear', 'best', 'regards', 'report', 'summary',
])
const COMMON_LOCATION_WORDS = new Set(['kingdom', 'france', 'spain', 'singapore', 'madrid', 'paris', 'london', 'manchester', 'oxford'])
const INLINE_WS_PATTERN = '[ \\t]+'
const NAME_TOKEN_PATTERN = "(?:[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+|[A-ZÀ-ÖØ-Ý]['’][A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+)(?:[-'’][A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+)*"
const INITIAL_TOKEN_PATTERN = '[A-Z]\\.'
const INITIAL_OPTIONAL_DOT_PATTERN = '[A-Z]\\.?' 
const PERSON_FULL_NAME_PATTERN = `${NAME_TOKEN_PATTERN}(?:${INLINE_WS_PATTERN}${NAME_TOKEN_PATTERN}){1,2}`
const PERSON_INITIAL_LAST_PATTERN = `${INITIAL_OPTIONAL_DOT_PATTERN}${INLINE_WS_PATTERN}${NAME_TOKEN_PATTERN}`
const PERSON_FIRST_INITIAL_PATTERN = `${NAME_TOKEN_PATTERN}${INLINE_WS_PATTERN}${INITIAL_OPTIONAL_DOT_PATTERN}`
const ORG_WORD_PATTERN = "[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9&'’-]*"
const CITY_TOKEN_PATTERN = "[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'’-]+"
const ADDRESS_STREET_WORDS = '(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|Rue|Calle|Via|Strasse|Strada)'
const ADDRESS_CONNECTOR_WORDS = '(?:de|del|de la|du|des|di|da|la)'
const MONTH_NAME_PATTERN = '(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
const INITIAL_TOKEN_REGEX = /^[A-Z]\.$/
const INITIAL_OPTIONAL_DOT_REGEX = new RegExp(`^${INITIAL_OPTIONAL_DOT_PATTERN}$`)
const INITIAL_NAME_PATTERN = `${INITIAL_OPTIONAL_DOT_PATTERN}${INLINE_WS_PATTERN}${NAME_TOKEN_PATTERN}`
const PERSON_REFERENCE_PATTERN = `(?:${PERSON_FULL_NAME_PATTERN}|${PERSON_INITIAL_LAST_PATTERN}|${PERSON_FIRST_INITIAL_PATTERN})`
const PERSON_BOUNDARY_PATTERN = `(?=\\s|$|[),.;:"'”’])`
const NAME_TOKEN_REGEX = new RegExp(`^${NAME_TOKEN_PATTERN}$`)
const PERSON_TITLE_REGEX = /^(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+/
const PERSON_FULL_NAME_REGEX = new RegExp(`\\b(?:Mr|Mrs|Ms|Dr|Prof)\\.?${INLINE_WS_PATTERN}(?:${PERSON_FULL_NAME_PATTERN}|${PERSON_INITIAL_LAST_PATTERN}|${PERSON_FIRST_INITIAL_PATTERN})${PERSON_BOUNDARY_PATTERN}|\\b(?:${PERSON_FULL_NAME_PATTERN}|${PERSON_INITIAL_LAST_PATTERN}|${PERSON_FIRST_INITIAL_PATTERN})${PERSON_BOUNDARY_PATTERN}`, 'g')
const PERSON_SINGLE_NAME_REGEX = new RegExp(`\\b${NAME_TOKEN_PATTERN}\\b`, 'g')
const PHONE_VALUE_REGEX = /(?:\+?\d[\d\s().-]{7,}\d|\(\d{2,5}\)[\d\s.-]{5,}\d)/
const IPV4_VALUE_REGEX = /\b\d{1,3}(?:\.\d{1,3}){3}\b/
const IPV6_VALUE_REGEX = /\b(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}\b/
const AT_USERNAME_REGEX = /(?<![\w/])@\w[\w.-]+\b/g
const PLAIN_USERNAME_REGEX = /(?<![\w/])(?=[a-z0-9-]*[a-z])[a-z0-9]+-[a-z0-9-]+\b/g
const FILE_PATH_REGEX = /(?<!https:)(?<!http:)\/(?:[^\s/]+\/)+[^\s/]*/g
const WINDOWS_FILE_PATH_REGEX = /\b[A-Z]:\\(?:[^\\\s]+\\)*[^\\\s]+\b/g
const COORDINATE_REGEX = /\b\d{1,3}\.\d+\s*°?\s*[NS],\s*\d{1,3}\.\d+\s*°?\s*[EW]\b/gi
const API_KEY_OPENAI_REGEX = /\bsk-[A-Za-z0-9]{20,}\b/g
const API_KEY_AWS_REGEX = /\bAKIA[0-9A-Z]{16}\b/g
const API_KEY_GITHUB_REGEX = /\bgh[pousr]_[A-Za-z0-9]{36,}\b/g
const API_KEY_GOOGLE_REGEX = /\bAIza[0-9A-Za-z\-_]{35}\b/g
const API_KEY_LABELED_REGEX = /\b(?:[A-Z0-9_]*(?:OPENAI_KEY|API_KEY|SECRET|TOKEN|ACCESS_KEY|AWS_SECRET)[A-Z0-9_]*)\s*=\s*([A-Za-z0-9_-]{20,})\b/g
const CREDIT_CARD_REGEX = /\b(?:\d[ -]*?){13,16}\b/g
const GOVERNMENT_ID_SSN_REGEX = /\b\d{3}-\d{2}-\d{4}\b/g
const GOVERNMENT_ID_UK_NI_REGEX = /\b[A-Z]{2}\d{6}[A-Z]\b/g
const BANK_ACCOUNT_IBAN_REGEX = /\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b/g
const PRIVATE_KEY_BLOCK_REGEX = /-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----/g
const PRIVATE_KEY_HEADER_REGEX = /-----BEGIN (?:RSA )?PRIVATE KEY-----/g

function isPersonStopword(token) {
  return PERSON_STOPWORDS.has(String(token || '').toLowerCase())
}

function normalizedWords(value) {
  return String(value || '')
    .replace(/[^A-Za-z0-9' -]+/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.toLowerCase())
}

function hasOrgHint(text) {
  return isOrgLikePhrase(text)
}

function isOrgLikePhrase(value) {
  const words = normalizedWords(value)
  if (words.length === 0) return false
  if (ORG_PREFIX_WORDS.has(words[0]) && words[1] === 'of') return true
  return words.some((word) => ORG_HINT_WORDS.has(word) || ORG_SUFFIX_WORDS.has(word))
}

function isIgnoredEntityPhrase(value) {
  const words = normalizedWords(value)
  return IGNORED_ENTITY_PREFIXES.some((prefix) => prefix.every((word, index) => words[index] === word))
}

function isStreetLikePhrase(value) {
  const words = normalizedWords(value)
  if (words.length === 0) return false
  if (STREET_PREFIX_WORDS.has(words[0])) return true
  return STREET_SUFFIXES.has(words[words.length - 1])
}

function previousTokens(text, index, count = 3) {
  const words = text.slice(0, index).match(/[A-Za-z]+/g) || []
  return words.slice(-count).map((word) => word.toLowerCase())
}

function hasOrgPrefixContext(text, start) {
  const prev = previousTokens(text, start, 2)
  return prev.length === 2 && ORG_PREFIX_WORDS.has(prev[0]) && prev[1] === 'of'
}

function hasIgnoredEntityContext(text, start) {
  const prev = previousTokens(text, start, 2)
  return IGNORED_ENTITY_PREFIXES.some((prefix) => prefix.every((word, index) => prev[index] === word))
}

function stripPersonTitle(value) {
  return String(value || '').trim().replace(PERSON_TITLE_REGEX, '')
}

function normalizeEntityValue(type, value) {
  const base = type === 'PERSON' ? stripPersonTitle(value) : String(value || '')
  return base
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function isLikelyPhoneValue(value) {
  const candidate = String(value || '').trim()
  if (IPV4_VALUE_REGEX.test(candidate) || IPV6_VALUE_REGEX.test(candidate)) return false
  const digits = candidate.replace(/\D/g, '')
  return digits.length >= 8 && digits.length <= 15 && (digits.length >= 10 || candidate.includes('+') || /[\s.-]/.test(candidate))
}

function isApiKeyValue(value) {
  const candidate = String(value || '').trim()
  return /^sk-[A-Za-z0-9]{20,}$/.test(candidate)
    || /^AKIA[0-9A-Z]{16}$/.test(candidate)
    || /^gh[pousr]_[A-Za-z0-9]{36,}$/.test(candidate)
    || /^AIza[0-9A-Za-z\-_]{35}$/.test(candidate)
}

function extractApiKeyCandidate(value) {
  const candidate = String(value || '').trim()
  if (!candidate) return ''
  API_KEY_LABELED_REGEX.lastIndex = 0
  const labeled = API_KEY_LABELED_REGEX.exec(candidate)
  if (labeled) return labeled[1]
  const direct = candidate.match(API_KEY_OPENAI_REGEX) || candidate.match(API_KEY_AWS_REGEX) || candidate.match(API_KEY_GITHUB_REGEX) || candidate.match(API_KEY_GOOGLE_REGEX)
  return direct ? direct[0] : ''
}

function passesLuhn(value) {
  const digits = String(value || '').replace(/\D/g, '')
  if (digits.length < 13 || digits.length > 16) return false
  let total = 0
  const parity = digits.length % 2
  for (let i = 0; i < digits.length; i += 1) {
    let num = Number(digits[i])
    if (i % 2 === parity) {
      num *= 2
      if (num > 9) num -= 9
    }
    total += num
  }
  return total % 10 === 0
}

function getLineAt(text, index) {
  const safe = Math.min(Math.max(index, 0), Math.max(text.length - 1, 0))
  let start = safe
  let end = safe
  while (start > 0 && text[start - 1] !== '\n') start -= 1
  while (end < text.length && text[end] !== '\n') end += 1
  return text.slice(start, end)
}

function isLikelyHeadingLine(line) {
  const trimmed = String(line || '').trim()
  if (!trimmed) return false
  const normalized = trimmed
    .replace(/^(?:subject|title)\s*:\s*/i, '')
    .replace(/[–—-]/g, ' ')
    .trim()
  if (!normalized || normalized.length > 140) return false
  if (/[.!?]/.test(normalized)) return false
  const words = normalized.split(/\s+/).filter(Boolean)
  if (words.length < 2 || words.length > 12) return false
  if (['hi', 'hello', 'dear'].includes(words[0].toLowerCase())) return false
  const titleLike = words.filter((w) => /^[A-Z][A-Za-z0-9&'+-]*$/.test(w)).length
  const ratio = titleLike / words.length
  return (ratio >= 0.75 && words.length >= 4) || (ratio >= 0.9 && words.length >= 3)
}

function intersectsLocked(start, end, locked = []) {
  return locked.some((span) => !(end <= span.start || start >= span.end))
}

function nextWordAfter(text, endIdx) {
  const tail = text.slice(endIdx)
  const m = tail.match(/^\s+([A-Za-z]+)/)
  return m ? m[1].toLowerCase() : ''
}

function hasImmediateCapitalizedNextWord(text, endIdx) {
  const tail = text.slice(endIdx)
  return /^\s+[A-Z][a-z]{1,}(?:-[A-Z][a-z]{1,})*\b/.test(tail)
}

function isPersonCandidateValid(text, start, end, token) {
  if (!token || token.length < 3) return false
  const lowered = token.toLowerCase()
  if (isPersonStopword(token)) return false
  if (NON_PERSON_NAME_WORDS.has(lowered)) return false
  if (COMMON_CITY_WORDS.has(lowered)) return false
  if (NON_PERSON_SINGLE_BLOCK.has(lowered)) return false
  if (TECH_BLOCK_WORDS.has(lowered)) return false
  if (ORG_HINT_WORDS.has(lowered)) return false
  if (ORG_SUFFIX_WORDS.has(lowered)) return false
  if (STREET_PREFIX_WORDS.has(lowered)) return false
  if (!NAME_TOKEN_REGEX.test(token)) return false
  const next = nextWordAfter(text, end)
  if (STREET_SUFFIXES.has(next)) return false
  if (ORG_HINT_WORDS.has(next)) return false
  if (ORG_SUFFIX_WORDS.has(next)) return false
  if (TECH_BLOCK_WORDS.has(next)) return false
  if (hasIgnoredEntityContext(text, start)) return false
  if (hasOrgPrefixContext(text, start)) return false
  const line = getLineAt(text, start)
  if (isLikelyHeadingLine(line)) return false
  return true
}

function isPersonFullNameCandidateValid(text, start, end, phrase) {
  const cleaned = stripPersonTitle(phrase).replace(/\s+/g, ' ')
  const parts = cleaned.split(' ')
  if (parts.length < 2 || parts.length > 3) return false

  const first = parts[0]
  const last = parts[parts.length - 1]
  const middle = parts.slice(1, -1)
  const firstOk = NAME_TOKEN_REGEX.test(first) || INITIAL_OPTIONAL_DOT_REGEX.test(first)
  const lastOk = NAME_TOKEN_REGEX.test(last) || (parts.length === 2 && INITIAL_OPTIONAL_DOT_REGEX.test(last))
  if (!firstOk || !lastOk) return false
  if (parts.length === 3 && !middle.every((part) => NAME_TOKEN_REGEX.test(part))) return false

  const loweredParts = parts.map((part) => part.toLowerCase().replace(/\.$/, ''))
  const firstLower = loweredParts[0]
  const lastLower = loweredParts[loweredParts.length - 1]
  if (loweredParts.some((part) => NON_PERSON_NAME_WORDS.has(part))) return false
  if (COMMON_LOCATION_WORDS.has(firstLower) || COMMON_LOCATION_WORDS.has(lastLower)) return false
  if (parts.some((part) => isPersonStopword(part))) return false
  if (CTA_ACTION_WORDS.has(firstLower)) return false
  if (DISCOURSE_WORDS.has(firstLower) || DISCOURSE_WORDS.has(lastLower)) return false
  if (loweredParts.some((part) => TECH_BLOCK_WORDS.has(part))) return false
  if (loweredParts.some((part) => ORG_HINT_WORDS.has(part) || ORG_SUFFIX_WORDS.has(part))) return false
  if (STREET_PREFIX_WORDS.has(firstLower)) return false
  if (isStreetLikePhrase(cleaned)) return false
  if (hasIgnoredEntityContext(text, start)) return false
  if (hasOrgPrefixContext(text, start)) return false
  const next = nextWordAfter(text, end)
  if (ORG_SUFFIX_WORDS.has(next)) return false
  const line = getLineAt(text, start)
  const lineTrimmed = line.trim().replace(/\s+/g, ' ')
  if (isLikelyHeadingLine(line) && lineTrimmed !== cleaned) return false
  return true
}

function isPersonSpanValid(text, start, end, phrase) {
  const cleaned = stripPersonTitle(phrase).trim()
  if (!cleaned) return false
  if (cleaned.includes(' ')) return isPersonFullNameCandidateValid(text, start, end, phrase)
  return isPersonCandidateValid(text, start, end, cleaned)
}

function personSignature(cleaned) {
  const parts = String(cleaned || '').split(/\s+/).filter(Boolean)
  if (parts.length === 2) {
    const [first, last] = parts
    if (NAME_TOKEN_REGEX.test(first) && NAME_TOKEN_REGEX.test(last)) {
      return { kind: 'full', first: first.toLowerCase(), last: last.toLowerCase() }
    }
    if (INITIAL_OPTIONAL_DOT_REGEX.test(first) && NAME_TOKEN_REGEX.test(last)) {
      return { kind: 'initial_last', firstInitial: first[0].toLowerCase(), last: last.toLowerCase() }
    }
    if (NAME_TOKEN_REGEX.test(first) && INITIAL_OPTIONAL_DOT_REGEX.test(last)) {
      return { kind: 'first_initial', first: first.toLowerCase(), lastInitial: last[0].toLowerCase() }
    }
    return null
  }
  if (parts.length === 3 && parts.every((part) => NAME_TOKEN_REGEX.test(part))) {
    return { kind: 'full', first: parts[0].toLowerCase(), last: parts[2].toLowerCase() }
  }
  return null
}

const REGEX = {
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  API_KEY_OPENAI: /\bsk-[A-Za-z0-9]{20,}\b/g,
  API_KEY_AWS: /\bAKIA[0-9A-Z]{16}\b/g,
  API_KEY_GITHUB: /\bgh[pousr]_[A-Za-z0-9]{36,}\b/g,
  API_KEY_GOOGLE: /\bAIza[0-9A-Za-z\-_]{35}\b/g,
  API_KEY_LABELED: /\b(?:[A-Z0-9_]*(?:OPENAI_KEY|API_KEY|SECRET|TOKEN|ACCESS_KEY|AWS_SECRET)[A-Z0-9_]*)\s*=\s*([A-Za-z0-9_-]{20,})\b/g,
  PRIVATE_KEY_BLOCK: /-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----/g,
  PRIVATE_KEY_HEADER: /-----BEGIN (?:RSA )?PRIVATE KEY-----/g,
  CREDIT_CARD: /\b(?:\d[ -]*?){13,16}\b/g,
  GOVERNMENT_ID_SSN: /\b\d{3}-\d{2}-\d{4}\b/g,
  GOVERNMENT_ID_UK_NI: /\b[A-Z]{2}\d{6}[A-Z]\b/g,
  BANK_ACCOUNT_IBAN: /\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b/g,
  PHONE: /(?:\+?\d[\d\s().-]{7,}\d|\(\d{2,5}\)[\d\s.-]{5,}\d)/g,
  IP_ADDRESS_V4: /\b\d{1,3}(?:\.\d{1,3}){3}\b/g,
  IP_ADDRESS_V6: /\b(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}\b/g,
  URL: /https?:\/\/[^\s]+/gi,
  UK_REF: /\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b/gi,
  PASSPORT: /\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b/g,
  DATE: new RegExp(`\\b(?:\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}|\\d{1,2}-\\d{1,2}-\\d{2,4}|\\d{1,2}(?:st|nd|rd|th)?${INLINE_WS_PATTERN}${MONTH_NAME_PATTERN}${INLINE_WS_PATTERN}\\d{4}|${MONTH_NAME_PATTERN}${INLINE_WS_PATTERN}\\d{1,2}(?:st|nd|rd|th)?(?:,${INLINE_WS_PATTERN}|\\s+)\\d{4})\\b`, 'gi'),
  UK_POSTCODE: /\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/gi,
  ADDRESS_UK_FULL: new RegExp(`\\b\\d{1,5}[A-Za-z]?${INLINE_WS_PATTERN}(?:${NAME_TOKEN_PATTERN}${INLINE_WS_PATTERN}){0,4}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd|View)\\b(?:,\\s*[A-Z][A-Za-z' -]{1,40}\\s+[A-Z]{1,2}\\d[A-Z\\d]?\\s?\\d[A-Z]{2}\\b|,\\s*[A-Z][A-Za-z' -]{1,40}\\b)?`, 'g'),
  ADDRESS_EU_NUMBERED: new RegExp(`\\b\\d{1,5}[A-Za-z]?${INLINE_WS_PATTERN}(?:${ADDRESS_STREET_WORDS})(?:${INLINE_WS_PATTERN}(?:${ADDRESS_CONNECTOR_WORDS}|${CITY_TOKEN_PATTERN})){1,6}(?:,\\s*\\d{4,5}${INLINE_WS_PATTERN}${CITY_TOKEN_PATTERN}(?:${INLINE_WS_PATTERN}${CITY_TOKEN_PATTERN}){0,2})?\\b`, 'g'),
  ADDRESS_EU_TRAILING_NUMBER: new RegExp(`\\b(?:${ADDRESS_STREET_WORDS})(?:${INLINE_WS_PATTERN}(?:${ADDRESS_CONNECTOR_WORDS}|${CITY_TOKEN_PATTERN})){1,6}${INLINE_WS_PATTERN}\\d{1,5}[A-Za-z]?(?:,\\s*\\d{4,5}${INLINE_WS_PATTERN}${CITY_TOKEN_PATTERN}(?:${INLINE_WS_PATTERN}${CITY_TOKEN_PATTERN}){0,2})?\\b`, 'g'),
  ADDRESS_SG_BLOCK: new RegExp(`\\b(?:${ORG_WORD_PATTERN}|${CITY_TOKEN_PATTERN})(?:${INLINE_WS_PATTERN}(?:${ORG_WORD_PATTERN}|${CITY_TOKEN_PATTERN}|Financial|Centre|Center|Tower|Building|Plaza|Bay)){1,6}(?:\\s*(?:\\r?\\n|,\\s*)\\s*(?:Tower${INLINE_WS_PATTERN}\\d+|#${INLINE_WS_PATTERN}?\\d{1,2}-\\d{2}|Tower${INLINE_WS_PATTERN}\\d+${INLINE_WS_PATTERN}#\\d{1,2}-\\d{2}))?(?:\\s*(?:\\r?\\n|,\\s*)\\s*Singapore${INLINE_WS_PATTERN}\\d{6})\\b`, 'gi'),
  ADDRESS_POSTCODE_CITY: new RegExp(`\\b\\d{4,5}${INLINE_WS_PATTERN}${CITY_TOKEN_PATTERN}(?:${INLINE_WS_PATTERN}${CITY_TOKEN_PATTERN}){0,2}\\b`, 'g'),
  ADDRESS_VIA: new RegExp(`\\bVia${INLINE_WS_PATTERN}${NAME_TOKEN_PATTERN}(?:${INLINE_WS_PATTERN}${NAME_TOKEN_PATTERN}){0,2}\\b`, 'g'),
  COORDINATE: /\b\d{1,3}\.\d+\s*°?\s*[NS],\s*\d{1,3}\.\d+\s*°?\s*[EW]\b/gi,
  FILE_PATH: /(?<!https:)(?<!http:)\/(?:[^\s/]+\/)+[^\s/]*/g,
  FILE_PATH_WINDOWS: /\b[A-Z]:\\(?:[^\\\s]+\\)*[^\\\s]+\b/g,
}

const IMMIGRATION = /\b(visa|ukvi|uan|gwf|cas|cos|sponsor|brp|ilr|immigration|home office)\b/i
const SUPPORTED_LANGUAGE_CODE = 'en'
const SUPPORTED_LANGUAGE_LABEL = 'English'
const UNKNOWN_LANGUAGE_CODE = 'unknown'
const NON_ENGLISH_WARNING = 'This text appears to be non-English. Entity detection may be less accurate.'
const LANGUAGE_HINTS = {
  en: new Set(['the', 'and', 'is', 'are', 'was', 'were', 'with', 'from', 'that', 'this', 'have', 'has']),
  es: new Set(['el', 'la', 'de', 'que', 'hola', 'gracias', 'para', 'con', 'una', 'por', 'me', 'llamo', 'en', 'y']),
  fr: new Set(['le', 'la', 'de', 'bonjour', 'merci', 'avec', 'pour', 'une', 'dans', 'est', 'et', 'je', 'vous']),
  de: new Set(['der', 'die', 'das', 'und', 'mit', 'für', 'ist', 'nicht', 'ich', 'sie', 'ein', 'eine', 'den']),
  it: new Set(['il', 'lo', 'la', 'ciao', 'grazie', 'con', 'per', 'che', 'una', 'sono', 'non', 'nel', 'gli']),
  pt: new Set(['olá', 'ola', 'obrigado', 'com', 'para', 'que', 'uma', 'não', 'voce', 'você', 'está', 'em', 'de']),
  nl: new Set(['de', 'het', 'een', 'en', 'met', 'voor', 'niet', 'ik', 'je', 'dat', 'dit', 'van']),
}
const LANGUAGE_ACCENT_HINTS = {
  es: ['ñ', 'á', 'é', 'í', 'ó', 'ú'],
  fr: ['à', 'â', 'ç', 'è', 'é', 'ê', 'ë', 'î', 'ï', 'ô', 'ù', 'û', 'ü', 'œ'],
  de: ['ä', 'ö', 'ü', 'ß'],
  it: ['à', 'è', 'é', 'ì', 'ò', 'ù'],
  pt: ['ã', 'â', 'á', 'à', 'ç', 'é', 'ê', 'í', 'ó', 'ô', 'õ', 'ú'],
}
const TOKEN_META = {
  PERSON: { label: 'Person', emoji: '👤' },
  EMAIL: { label: 'Email', emoji: '📧' },
  API_KEY: { label: 'API Key', emoji: '🔑' },
  CREDIT_CARD: { label: 'Credit Card', emoji: '💳' },
  GOVERNMENT_ID: { label: 'Government ID', emoji: '🪪' },
  BANK_ACCOUNT: { label: 'Bank Account', emoji: '🏦' },
  PRIVATE_KEY: { label: 'Private Key', emoji: '🔐' },
  PHONE: { label: 'Phone', emoji: '📞' },
  IP_ADDRESS: { label: 'IP Address', emoji: '🌐' },
  ADDRESS: { label: 'Location', emoji: '📍' },
  ORG: { label: 'Organisation', emoji: '🏢' },
  DATE: { label: 'Date', emoji: '📅' },
  URL: { label: 'Web Address', emoji: '🔗' },
  USERNAME: { label: 'Username', emoji: '🏷' },
  COORDINATE: { label: 'Coordinate', emoji: '🧭' },
  FILE_PATH: { label: 'File Path', emoji: '🗂' },
}
const ENTITY_PRIORITY = {
  EMAIL: 0,
  URL: 1,
  API_KEY: 2,
  PRIVATE_KEY: 3,
  CREDIT_CARD: 4,
  GOVERNMENT_ID: 5,
  BANK_ACCOUNT: 6,
  IP_ADDRESS: 7,
  PHONE: 8,
  ADDRESS: 9,
  DATE: 10,
  ORG: 11,
  PERSON: 12,
  USERNAME: 13,
  COORDINATE: 14,
  FILE_PATH: 15,
}

export function detectLanguage(text) {
  const cleaned = String(text || '').replace(/https?:\/\/\S+|\b\S+@\S+\b|\d+/g, ' ')
  const letters = Array.from(cleaned).filter((char) => /\p{L}/u.test(char))
  if (letters.length === 0) return SUPPORTED_LANGUAGE_CODE

  const scriptCounts = {
    ru: (cleaned.match(/[Ѐ-ӿ]/g) || []).length,
    ar: (cleaned.match(/[\u0600-\u06FF]/g) || []).length,
    zh: (cleaned.match(/[\u4E00-\u9FFF]/g) || []).length,
    ja: (cleaned.match(/[\u3040-\u30FF]/g) || []).length,
  }
  const scriptThreshold = Math.max(2, Math.floor(letters.length * 0.2))
  for (const [code, count] of Object.entries(scriptCounts)) {
    if (count >= scriptThreshold) return code
  }

  const words = cleaned.toLowerCase().match(/[a-zà-öø-ÿ']+/gi) || []
  if (words.length < 4) return UNKNOWN_LANGUAGE_CODE

  const scores = Object.fromEntries(
    Object.entries(LANGUAGE_HINTS).map(([code, hints]) => {
      let score = words.reduce((total, word) => total + (hints.has(word) ? 1 : 0), 0)
      for (const marker of LANGUAGE_ACCENT_HINTS[code] || []) {
        if (cleaned.toLowerCase().includes(marker)) score += 1
      }
      return [code, score]
    })
  )

  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1])
  const [bestCode, bestScore] = ranked[0]
  const runnerUp = ranked[1]?.[1] || 0
  if (bestScore >= 2 && bestScore >= runnerUp + 1) return bestCode
  return UNKNOWN_LANGUAGE_CODE
}

export function getLanguageWarning(text) {
  const detectedLanguage = detectLanguage(text)
  return {
    warning: detectedLanguage !== SUPPORTED_LANGUAGE_CODE && detectedLanguage !== UNKNOWN_LANGUAGE_CODE ? NON_ENGLISH_WARNING : null,
    detected_language: detectedLanguage,
    supported_language: SUPPORTED_LANGUAGE_LABEL,
  }
}

function shouldApplyPronounReversal(text) {
  const language = detectLanguage(text)
  if (language === SUPPORTED_LANGUAGE_CODE) return true
  if (language !== UNKNOWN_LANGUAGE_CODE) return false

  const words = String(text || '').toLowerCase().match(/[a-zà-öø-ÿ']+/gi) || []
  if (words.length === 0) return false

  const englishScore = words.reduce((total, word) => (
    total + (LANGUAGE_HINTS.en.has(word) || PRONOUN_ENGLISH_HINTS.has(word) ? 1 : 0)
  ), 0)

  let foreignScore = 0
  for (const [code, hints] of Object.entries(LANGUAGE_HINTS)) {
    if (code === SUPPORTED_LANGUAGE_CODE) continue
    foreignScore = Math.max(foreignScore, words.reduce((total, word) => total + (hints.has(word) ? 1 : 0), 0))
  }
  return englishScore > 0 && englishScore >= foreignScore + 1
}

function detectRegex(text, enabled) {
  const out = []
  const add = (type, regex, score = 0.99) => {
    if (!enabled.has(type)) return
    regex.lastIndex = 0
    let m
    while ((m = regex.exec(text)) !== null) {
      let start = m.index
      let end = m.index + m[0].length
      // Include leading '+' for phone values like +44 7700 900123.
      if (type === 'PHONE' && start > 0 && text[start - 1] === '+') {
        start -= 1
      }
      if (type === 'PHONE' && !isLikelyPhoneValue(text.slice(start, end))) {
        continue
      }
      out.push({ type, start, end, score })
    }
  }

  add('EMAIL', REGEX.EMAIL)
  add('URL', REGEX.URL)
  add('API_KEY', REGEX.API_KEY_OPENAI)
  add('API_KEY', REGEX.API_KEY_AWS)
  add('API_KEY', REGEX.API_KEY_GITHUB)
  add('API_KEY', REGEX.API_KEY_GOOGLE)
  if (enabled.has('API_KEY')) {
    REGEX.API_KEY_LABELED.lastIndex = 0
    let labeled
    while ((labeled = REGEX.API_KEY_LABELED.exec(text)) !== null) {
      const value = labeled[1]
      const start = labeled.index + labeled[0].lastIndexOf(value)
      out.push({ type: 'API_KEY', start, end: start + value.length, score: 0.995 })
    }
  }
  add('PRIVATE_KEY', REGEX.PRIVATE_KEY_BLOCK)
  add('PRIVATE_KEY', REGEX.PRIVATE_KEY_HEADER)
  add('GOVERNMENT_ID', REGEX.GOVERNMENT_ID_SSN)
  add('GOVERNMENT_ID', REGEX.GOVERNMENT_ID_UK_NI)
  add('BANK_ACCOUNT', REGEX.BANK_ACCOUNT_IBAN)
  const addValidated = (type, regex, validator, score = 0.99) => {
    if (!enabled.has(type)) return
    regex.lastIndex = 0
    let m
    while ((m = regex.exec(text)) !== null) {
      if (!validator(m[0])) continue
      out.push({ type, start: m.index, end: m.index + m[0].length, score })
    }
  }
  addValidated('CREDIT_CARD', REGEX.CREDIT_CARD, passesLuhn)
  add('IP_ADDRESS', REGEX.IP_ADDRESS_V4)
  add('IP_ADDRESS', REGEX.IP_ADDRESS_V6)
  add('PHONE', REGEX.PHONE)

  if (enabled.has('ADDRESS')) {
    // Prefer full address spans first to avoid partial leaks.
    REGEX.ADDRESS_UK_FULL.lastIndex = 0
    let m
    while ((m = REGEX.ADDRESS_UK_FULL.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.995 })
    }

    for (const key of ['ADDRESS_EU_NUMBERED', 'ADDRESS_EU_TRAILING_NUMBER']) {
      REGEX[key].lastIndex = 0
      while ((m = REGEX[key].exec(text)) !== null) {
        out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.985 })
      }
    }

    REGEX.ADDRESS_SG_BLOCK.lastIndex = 0
    while ((m = REGEX.ADDRESS_SG_BLOCK.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.982 })
    }

    REGEX.ADDRESS_VIA.lastIndex = 0
    while ((m = REGEX.ADDRESS_VIA.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.97 })
    }

    // Capture city + postcode chunks even when street portion is missing/ambiguous.
    const cityPostcode = /\b[A-Z][A-Za-z' -]{1,40}\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/g
    while ((m = cityPostcode.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.96 })
    }

    REGEX.ADDRESS_POSTCODE_CITY.lastIndex = 0
    while ((m = REGEX.ADDRESS_POSTCODE_CITY.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.955 })
    }

    for (const key of ['UK_REF', 'PASSPORT']) {
      REGEX[key].lastIndex = 0
      while ((m = REGEX[key].exec(text)) !== null) {
        out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.95 })
      }
    }
  }

  add('DATE', REGEX.DATE)
  add('COORDINATE', REGEX.COORDINATE)
  add('FILE_PATH', REGEX.FILE_PATH)
  add('FILE_PATH', REGEX.FILE_PATH_WINDOWS)

  return out
}

function detectStructuredFields(text, enabled) {
  const out = []
  const lines = text.split('\n')
  let offset = 0

  const labelMap = {
    person: 'PERSON',
    email: 'EMAIL',
    phone: 'PHONE',
    address: 'ADDRESS',
    organisation: 'ORG',
    organization: 'ORG',
    date: 'DATE',
    url: 'URL',
    website: 'URL',
    webaddress: 'URL',
    apikey: 'API_KEY',
    creditcard: 'CREDIT_CARD',
    governmentid: 'GOVERNMENT_ID',
    bankaccount: 'BANK_ACCOUNT',
    privatekey: 'PRIVATE_KEY',
    slack: 'USERNAME',
    github: 'USERNAME',
    username: 'USERNAME',
    handle: 'USERNAME',
    ip: 'IP_ADDRESS',
    serverip: 'IP_ADDRESS',
    ipv4: 'IP_ADDRESS',
    ipv6: 'IP_ADDRESS',
    backupipv6: 'IP_ADDRESS',
    coordinate: 'COORDINATE',
    coordinates: 'COORDINATE',
    filepath: 'FILE_PATH',
    path: 'FILE_PATH',
  }

  for (const line of lines) {
    const m = line.match(/^\s*([A-Za-z][A-Za-z ]{0,32})\s*(?::|->|→)\s*(.+?)\s*$/)
    if (m) {
      const label = m[1].toLowerCase().replace(/\s+/g, '')
      const mapped = labelMap[label]
      if (mapped && enabled.has(mapped)) {
        const value = m[2]
        const valueStartInLine = line.indexOf(value)
        if (valueStartInLine >= 0) {
          if (mapped === 'PERSON') {
            const personInList = new RegExp(`(?:Mr|Mrs|Ms|Dr|Prof)\\.?${INLINE_WS_PATTERN}(?:${PERSON_REFERENCE_PATTERN})(?=\\s|$|[),.;:])|(?:${PERSON_REFERENCE_PATTERN})(?=\\s|$|[),.;:])`, 'g')
            let pm
            while ((pm = personInList.exec(value)) !== null) {
              const token = pm[0]
              const start = offset + valueStartInLine + pm.index
              const end = start + token.length
              if (!isPersonSpanValid(text, start, end, token)) continue
              out.push({ type: mapped, start, end, score: 0.995 })
            }
          } else {
            const extractedValue = extractLabeledValue(value, mapped)
            if (!extractedValue) {
              offset += line.length + 1
              continue
            }
            const extractedOffset = line.indexOf(extractedValue, valueStartInLine)
            if (extractedOffset < 0) {
              offset += line.length + 1
              continue
            }
            out.push({
              type: mapped,
              start: offset + extractedOffset,
              end: offset + extractedOffset + extractedValue.length,
              score: 0.995,
            })
          }
        }
      }
    }
    offset += line.length + 1
  }
  return out
}

function extractLabeledValue(segment, type) {
  if (!segment) return ''
  const trimBoundaryPunctuation = (value) => String(value || '').replace(/[),.;:]+$/g, '').trim()
  if (type === 'EMAIL') {
    const m = segment.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/)
    return m ? m[0] : ''
  }
  if (type === 'URL') {
    const m = segment.match(/https?:\/\/[^\s,;]+/i)
    return m ? m[0] : ''
  }
  if (type === 'API_KEY') {
    return extractApiKeyCandidate(segment)
  }
  if (type === 'PRIVATE_KEY') {
    const m = segment.match(PRIVATE_KEY_BLOCK_REGEX) || segment.match(PRIVATE_KEY_HEADER_REGEX)
    return m ? m[0] : ''
  }
  if (type === 'CREDIT_CARD') {
    const m = segment.match(CREDIT_CARD_REGEX)
    return m && passesLuhn(m[0]) ? m[0] : ''
  }
  if (type === 'GOVERNMENT_ID') {
    const m = segment.match(GOVERNMENT_ID_SSN_REGEX) || segment.match(GOVERNMENT_ID_UK_NI_REGEX)
    return m ? m[0] : ''
  }
  if (type === 'BANK_ACCOUNT') {
    const m = segment.match(BANK_ACCOUNT_IBAN_REGEX)
    return m ? m[0] : ''
  }
  if (type === 'PHONE') {
    const m = segment.match(PHONE_VALUE_REGEX)
    return m ? m[0].trim() : ''
  }
  if (type === 'IP_ADDRESS') {
    const m = segment.match(IPV4_VALUE_REGEX) || segment.match(IPV6_VALUE_REGEX)
    return m ? m[0] : ''
  }
  if (type === 'DATE') {
    const m = segment.match(REGEX.DATE)
    return m ? m[0] : ''
  }
  if (type === 'USERNAME') {
    const atHandle = segment.match(/@\w[\w.-]+/)
    if (atHandle) return atHandle[0]
    const hyphenHandle = segment.match(/\b[a-z0-9]+-[a-z0-9-]+\b/)
    return hyphenHandle ? hyphenHandle[0] : ''
  }
  if (type === 'COORDINATE') {
    const m = segment.match(COORDINATE_REGEX)
    return m ? m[0] : ''
  }
  if (type === 'FILE_PATH') {
    const m = segment.match(FILE_PATH_REGEX) || segment.match(WINDOWS_FILE_PATH_REGEX)
    return m ? m[0] : ''
  }
  if (type === 'PERSON') {
    PERSON_FULL_NAME_REGEX.lastIndex = 0
    const m = PERSON_FULL_NAME_REGEX.exec(segment)
    return m ? m[0] : ''
  }
  if (type === 'ORG') {
    const stop = segment.search(/(?:,\s*(?:Date|Person|Email|Phone|Address|Organisation|Organization)\b|[.;]\s)/)
    return trimBoundaryPunctuation(stop >= 0 ? segment.slice(0, stop) : segment)
  }
  if (type === 'ADDRESS') {
    const stop = segment.search(/(?:,\s*(?:Organisation|Organization|Date|Person|Email|Phone|Address)\b|[.;]\s)/)
    return trimBoundaryPunctuation(stop >= 0 ? segment.slice(0, stop) : segment)
  }
  return segment
}

function detectHeuristics(text, enabled, locked = []) {
  const out = []
  if (enabled.has('PERSON')) {
    // Narrative single-name cues: "named Liam", "called Sarah".
    const namedOrCalled = new RegExp(`\\b(named|called)\\s+(${PERSON_REFERENCE_PATTERN})\\b`, 'gi')
    let m
    while ((m = namedOrCalled.exec(text)) !== null) {
      const name = m[2]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.86 })
    }

    // Role + Name cues: "analyst Liam", "engineer Sarah".
    const roleName = new RegExp(`\\b(?:analyst|engineer|developer|researcher|assistant|manager|consultant|officer|intern)\\s+(${PERSON_REFERENCE_PATTERN})\\b`, 'gi')
    while ((m = roleName.exec(text)) !== null) {
      const name = m[1]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.83 })
    }

    // Clause subject cue: "that Sarah joined...", "that Liam wrote...".
    const thatSubject = new RegExp(`\\bthat\\s+(${PERSON_REFERENCE_PATTERN})\\s+(is|was|has|had|works|worked|lives|lived|moved|joined|arrived|said|wrote)\\b`, 'g')
    while ((m = thatSubject.exec(text)) !== null) {
      const name = m[1]
      const verb = m[2].toLowerCase()
      if (!PERSON_SUBJECT_VERBS.has(verb)) continue
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.81 })
    }

    const thatInOffice = new RegExp(`\\bthat\\s+(${PERSON_REFERENCE_PATTERN})\\s+in\\s+(?:the\\s+)?[A-Za-z' -]{0,40}\\boffice\\b`, 'gi')
    while ((m = thatInOffice.exec(text)) !== null) {
      const name = m[1]
      const start = m.index + m[0].indexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.8 })
    }

    PERSON_FULL_NAME_REGEX.lastIndex = 0
    const person = PERSON_FULL_NAME_REGEX
    while ((m = person.exec(text)) !== null) {
      const start = m.index
      const end = m.index + m[0].length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonFullNameCandidateValid(text, start, end, m[0])) continue
      const parts = stripPersonTitle(m[0]).replace(/\./g, '').split(/\s+/).filter(Boolean)
      const hasBadPart = parts.some((p) => isPersonStopword(p))
      const orgish = hasOrgHint(m[0])
      if (hasBadPart || orgish) continue
      out.push({ type: 'PERSON', start, end, score: 0.8 })
    }

    // Relationship context: "his son Brian", "their manager Daniel".
    const rel = new RegExp(`\\b(?:his|her|their)\\s+(son|daughter|colleague|manager|supervisor|friend)\\s+(${PERSON_REFERENCE_PATTERN})\\b`, 'gi')
    while ((m = rel.exec(text)) !== null) {
      const relation = m[1].toLowerCase()
      const name = m[2]
      if (!PERSON_REL_WORDS.has(relation)) continue
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.84 })
    }

    // Communication verbs: "emailed Anna", "called Daniel", "spoke to Ravi".
    const comm = new RegExp(`\\b(emailed|called|met|contacted|messaged|spoke)\\s+(?:to\\s+)?(${PERSON_REFERENCE_PATTERN})\\b`, 'g')
    while ((m = comm.exec(text)) !== null) {
      const verb = m[1].toLowerCase()
      const name = m[2]
      if (!PERSON_CONTEXT_VERBS.has(verb)) continue
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      // Avoid partial replacement when a full name is present (e.g., "emailed Daniel Hughes").
      if (!name.includes(' ') && hasImmediateCapitalizedNextWord(text, end)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.82 })
    }

    // Self/owner intro: "my name is Nima", "his name is Brian".
    const intro = new RegExp(`\\b(my|his|her|their)\\s+name\\s+is\\s+(${PERSON_REFERENCE_PATTERN})\\b`, 'gi')
    while ((m = intro.exec(text)) !== null) {
      const name = m[2]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.85 })
    }

    // Relationship-owned intro: "wife's name is Julia", "partner's name is Dan".
    const introRelation = new RegExp(`\\b(?:wife|husband|partner|mother|father|brother|sister|friend|colleague|manager)['’]s\\s+name\\s+is\\s+(${PERSON_REFERENCE_PATTERN})\\b`, 'gi')
    while ((m = introRelation.exec(text)) !== null) {
      const name = m[1]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.84 })
    }

    // Subject form at sentence start: "Dan has ...", "Sofia works ...".
    const subjectLead = new RegExp(`(?:^|[.!?]\\s+)(${PERSON_REFERENCE_PATTERN})\\s+(is|was|has|had|works|worked|lives|lived|moved|joined|arrived|said|wrote)\\b`, 'g')
    while ((m = subjectLead.exec(text)) !== null) {
      const name = m[1]
      const verb = m[2].toLowerCase()
      if (!PERSON_SUBJECT_VERBS.has(verb)) continue
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.8 })
    }

    const conversationalFrom = new RegExp(`\\b(?:notes|message|comment)${INLINE_WS_PATTERN}from${INLINE_WS_PATTERN}((?:${PERSON_FULL_NAME_PATTERN}|${NAME_TOKEN_PATTERN}))\\b`, 'gi')
    while ((m = conversationalFrom.exec(text)) !== null) {
      const name = m[1]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (hasOrgHint(name) || isStreetLikePhrase(name) || isIgnoredEntityPhrase(name)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.88 })
    }
  }

  if (enabled.has('ORG')) {
    const org = new RegExp(`\\b${ORG_WORD_PATTERN}(?:${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}){0,5}${INLINE_WS_PATTERN}(?:Ltd\\.?|Limited|Inc\\.?|LLC|Consulting|Initiative|University|Lab|Labs|Institute|Instituto|School|Faculty|Foundation|Alliance|Group|Network|Agency|Council|Bank|Office|Department|Systems?|Analytics)\\b`, 'g')
    let m
    while ((m = org.exec(text)) !== null) {
      if (m[0].includes(' from ')) continue
      if (isIgnoredEntityPhrase(m[0]) || hasIgnoredEntityContext(text, m.index)) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.75 })
    }

    const orgDepartmental = new RegExp(`\\b(?:Department|Institute|School|Faculty|Centre|Center)${INLINE_WS_PATTERN}(?:of|for)${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}(?:${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}){0,5}\\b`, 'g')
    while ((m = orgDepartmental.exec(text)) !== null) {
      if (isIgnoredEntityPhrase(m[0])) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.93 })
    }

    const orgLeading = new RegExp(`\\b(?:University|Institute|Instituto|Lab|Labs)${INLINE_WS_PATTERN}(?:(?:of|for|de|del)${INLINE_WS_PATTERN})?${ORG_WORD_PATTERN}(?:${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}){0,4}\\b`, 'g')
    while ((m = orgLeading.exec(text)) !== null) {
      if (isIgnoredEntityPhrase(m[0]) || hasIgnoredEntityContext(text, m.index)) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.91 })
    }

    const orgExtended = new RegExp(`\\b${ORG_WORD_PATTERN}(?:${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}){0,5}${INLINE_WS_PATTERN}(?:Lab|Labs|Research|Initiative|Alliance|Group|Institute|Network|Foundation|Analytics)\\b`, 'g')
    while ((m = orgExtended.exec(text)) !== null) {
      if (isIgnoredEntityPhrase(m[0]) || hasIgnoredEntityContext(text, m.index)) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.82 })
    }

    const orgTech = /\b[A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,3}\s(?:AI|GenAI|Cloud|Security|Platform|Systems?|Services?|Solutions?|Teams|Drive|Jira|Workspace|Suite)\b/g
    while ((m = orgTech.exec(text)) !== null) {
      if (isIgnoredEntityPhrase(m[0]) || hasIgnoredEntityContext(text, m.index)) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.9 })
    }

    // Context-aware single-token organisations:
    // "working in Google", "joined Databricks", "at Anthropic".
    const orgContextualSingle = /\b(?:at|with|for|from|of|into|joined|joining|works(?:\s+at)?|worked(?:\s+at)?|working(?:\s+at)?|employed(?:\s+at)?)\s+([A-Z][A-Za-z0-9&.'’-]{2,}|[A-Z]{2,})\b/g
    while ((m = orgContextualSingle.exec(text)) !== null) {
      const candidate = m[1]
      const start = m.index + m[0].lastIndexOf(candidate)
      const end = start + candidate.length
      const prefix = text.slice(Math.max(0, m.index - 40), start).toLowerCase()
      if (hasIgnoredEntityContext(text, start)) continue
      if (intersectsLocked(start, end, locked)) continue
      if (/\b(?:notes|message|comment)\s+from\s+$/.test(prefix)) continue
      const lower = candidate.toLowerCase()
      if (FIELD_LABEL_WORDS.has(lower)) continue
      if (PERSON_STOPWORDS.has(lower)) continue
      if (STREET_SUFFIXES.has(lower)) continue
      if (COMMON_LOCATION_WORDS.has(lower)) continue
      if (PERSON_REL_WORDS.has(lower)) continue
      if (ORG_CONTEXT_WORDS.has(lower)) continue
      if (STREET_SUFFIXES.has(nextWordAfter(text, end))) continue
      if (hasImmediateCapitalizedNextWord(text, end) && !ORG_HINT_WORDS.has(lower) && !ORG_SUFFIX_WORDS.has(lower)) continue
      const line = getLineAt(text, start)
      if (isLikelyHeadingLine(line)) continue
      out.push({ type: 'ORG', start, end, score: 0.86 })
    }

    const orgParenthetical = new RegExp(`\\((${ORG_WORD_PATTERN}(?:${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}){0,3})\\)`, 'g')
    while ((m = orgParenthetical.exec(text)) !== null) {
      const candidate = m[1]
      const start = m.index + m[0].indexOf(candidate)
      const end = start + candidate.length
      if (hasIgnoredEntityContext(text, start)) continue
      if (intersectsLocked(start, end, locked)) continue
      const lower = candidate.toLowerCase()
      if (FIELD_LABEL_WORDS.has(lower)) continue
      if (PERSON_STOPWORDS.has(lower)) continue
      if (STREET_SUFFIXES.has(lower) || STREET_PREFIX_WORDS.has(lower)) continue
      if (COMMON_LOCATION_WORDS.has(lower)) continue
      if (isStreetLikePhrase(candidate) || isIgnoredEntityPhrase(candidate)) continue
      if (hasImmediateCapitalizedNextWord(text, end) && !ORG_HINT_WORDS.has(lower) && !ORG_SUFFIX_WORDS.has(lower)) continue
      out.push({ type: 'ORG', start, end, score: 0.84 })
    }
  }

  return out
}

function detectLateLocationCues(text, locked = []) {
  const out = []
  const locationCue = /\b(?:in|at|location\s+called)\s+([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b/g
  let m
  while ((m = locationCue.exec(text)) !== null) {
    const place = m[1]
    const idx = m.index + m[0].lastIndexOf(place)
    const end = idx + place.length
    if (intersectsLocked(idx, end, locked)) continue
    if (isPersonStopword(place)) continue
    if (hasOrgHint(place)) continue
    out.push({ type: 'ADDRESS', start: idx, end, score: 0.69 })
  }
  return out
}

function detectUsernames(text, enabled, locked = []) {
  if (!enabled.has('USERNAME')) return []
  const out = []

  AT_USERNAME_REGEX.lastIndex = 0
  let m
  while ((m = AT_USERNAME_REGEX.exec(text)) !== null) {
    const start = m.index
    const end = start + m[0].length
    if (intersectsLocked(start, end, locked)) continue
    out.push({ type: 'USERNAME', start, end, score: 0.97 })
  }

  const labeledHandle = /\b(?:Slack|GitHub|Github|Username|Handle)\s*:\s*([a-z0-9][\w.-]*|[a-z0-9]+-[a-z0-9-]+)\b/gi
  while ((m = labeledHandle.exec(text)) !== null) {
    const handle = m[1]
    const start = m.index + m[0].lastIndexOf(handle)
    const end = start + handle.length
    if (intersectsLocked(start, end, locked)) continue
    out.push({ type: 'USERNAME', start, end, score: 0.975 })
  }

  PLAIN_USERNAME_REGEX.lastIndex = 0
  while ((m = PLAIN_USERNAME_REGEX.exec(text)) !== null) {
    const start = m.index
    const end = start + m[0].length
    if (intersectsLocked(start, end, locked)) continue
    if (isApiKeyValue(m[0])) continue
    out.push({ type: 'USERNAME', start, end, score: 0.965 })
  }

  return out
}

function detectPersonFromOrganisationPattern(text, enabled, locked = []) {
  const out = []
  const personEnabled = enabled.has('PERSON')
  const orgEnabled = enabled.has('ORG')
  if (!personEnabled && !orgEnabled) return out

  const pattern = new RegExp(`\\b(${PERSON_REFERENCE_PATTERN})${INLINE_WS_PATTERN}from${INLINE_WS_PATTERN}(${ORG_WORD_PATTERN}(?:${INLINE_WS_PATTERN}${ORG_WORD_PATTERN}){0,6}${INLINE_WS_PATTERN}(?:Ltd\\.?|Limited|Inc\\.?|LLC|Consulting|University|Bank|Council|Office|Agency|Department|School|Faculty|Lab|Labs|Research|Initiative|Alliance|Group|Institute|Instituto|Network|Foundation|Systems?|Analytics))\\b`, 'g')
  let m
  while ((m = pattern.exec(text)) !== null) {
    const person = m[1]
    const org = m[2].trim()
    const personStart = m.index + m[0].indexOf(person)
    const personEnd = personStart + person.length
    const orgStart = m.index + m[0].indexOf(org)
    const orgEnd = orgStart + org.length

    // Ignore cases like "Anna Carter from Org", where captured person would be "Carter".
    const prevRaw = text.slice(0, personStart).match(/([A-Za-z]+)\W*$/)?.[1] || ''
    const precededByCapitalizedName = /^[A-Z][a-z]{2,}$/.test(prevRaw)

    if (personEnabled && !precededByCapitalizedName && !intersectsLocked(personStart, personEnd, locked) && isPersonSpanValid(text, personStart, personEnd, person)) {
      out.push({ type: 'PERSON', start: personStart, end: personEnd, score: 0.9 })
    }

    if (orgEnabled && !intersectsLocked(orgStart, orgEnd, locked)) {
      const first = (org.split(/\s+/)[0] || '').toLowerCase()
      if (!FIELD_LABEL_WORDS.has(first)) {
        out.push({ type: 'ORG', start: orgStart, end: orgEnd, score: 0.92 })
      }
    }
  }

  return out
}

function resolveOverlaps(detections) {
  const ranked = [...detections].sort((a, b) => {
    const priorityA = ENTITY_PRIORITY[a.type] ?? 99
    const priorityB = ENTITY_PRIORITY[b.type] ?? 99
    if (priorityA !== priorityB) return priorityA - priorityB
    const lenA = a.end - a.start
    const lenB = b.end - b.start
    if (lenA !== lenB) return lenB - lenA
    if (a.score !== b.score) return b.score - a.score
    if (a.start !== b.start) return a.start - b.start
    return a.end - b.end
  })

  const chosen = []
  for (const d of ranked) {
    const overlap = chosen.some((c) => !(d.end <= c.start || d.start >= c.end))
    if (!overlap) chosen.push(d)
  }

  return chosen.sort((a, b) => a.start - b.start || a.end - b.end)
}

function overlapsAny(det, chosen) {
  return chosen.some((c) => !(det.end <= c.start || det.start >= c.end))
}

function makeToken(type, index, style) {
  const meta = TOKEN_META[type] || { label: type, emoji: '🔒' }
  if (style === 'emoji') {
    return `[${meta.emoji} ${meta.label} ${index}]`
  }
  return `[${meta.label} ${index}]`
}

function canonicalEntityKey(type, value) {
  return `${type}:${normalizeEntityValue(type, value)}`
}

function applyReplacements(text, detections, tokenStyle = 'standard', aliasMap = {}) {
  const counters = {}
  const stableMap = {}
  const entities = []
  const out = []
  let i = 0

  for (const d of detections) {
    const original = text.slice(d.start, d.end)
    const ownCanonical = canonicalEntityKey(d.type, original)
    const canonical = aliasMap[ownCanonical] || ownCanonical
    let replacement = stableMap[canonical]
    if (!replacement) {
      counters[d.type] = (counters[d.type] || 0) + 1
      replacement = makeToken(d.type, counters[d.type], tokenStyle)
      stableMap[canonical] = replacement
    }
    out.push(text.slice(i, d.start))
    out.push(replacement)
    entities.push({ type: d.type, start: d.start, end: d.end, replacement, confidence: Number(d.score.toFixed(3)) })
    i = d.end
  }

  out.push(text.slice(i))
  const raw = out.join('')
  // Defensive cleanup: if a UK postcode fragment survives right after a location token,
  // collapse it to the location token to avoid leakage (e.g. "Location 11 4AB").
  const cleaned = raw
    .replace(/(\[(?:📍\s*)?Location\s+\d+\])\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/g, '$1')
    .replace(/(\[(?:📍\s*)?Location\s+\d+\])\s+\d\s+[A-Z]{2}\b/g, '$1')
  return { anonymized_text: cleaned, entities, counts: counters }
}

const PRONOUN_REVERSE_MAP = {
  she: 'he',
  he: 'she',
  him: 'her',
  her: 'him',
  his: 'her',
  hers: 'his',
}
const PRONOUN_REVERSE_REGEX = /\b(hers|his|him|her|she|he)\b/gi
const PRONOUN_PROTECTED_REGEX = /```[\s\S]*?```|`[^`\n]+`|\[[^\]\n]{1,120}\]|\bhttps?:\/\/[^\s]+\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/gi
const PRONOUN_ENGLISH_HINTS = new Set(Object.keys(PRONOUN_REVERSE_MAP))
const NON_POSSESSIVE_HER_FOLLOWERS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'being', 'but', 'by',
  'can', 'could', 'did', 'do', 'does', 'for', 'from', 'had', 'has', 'have',
  'if', 'in', 'into', 'is', 'may', 'might', 'must', 'nor', 'not', 'of', 'on',
  'or', 'should', 'than', 'that', 'the', 'their', 'them', 'then', 'there',
  'these', 'they', 'this', 'those', 'to', 'was', 'were', 'will', 'with', 'would',
  'yesterday', 'today', 'tomorrow', 'now', 'later', 'soon', 'here', 'back', 'again',
])

function applyCaseStyle(source, target) {
  if (!source) return target
  if (source === source.toUpperCase()) return target.toUpperCase()
  if (source === source.toLowerCase()) return target.toLowerCase()
  const isTitleCase = source[0] === source[0].toUpperCase() && source.slice(1) === source.slice(1).toLowerCase()
  if (isTitleCase) return target[0].toUpperCase() + target.slice(1).toLowerCase()
  return target
}

function replacementForReversedPronoun(segment, match, offset) {
  const lowered = match.toLowerCase()
  if (lowered === 'her') {
    const tail = segment.slice(offset + match.length)
    const nextMatch = tail.match(/^\s+([A-Za-zÀ-ÖØ-öø-ÿ']+)/)
    const nextWord = nextMatch ? nextMatch[1].toLowerCase() : ''
    return nextWord && !NON_POSSESSIVE_HER_FOLLOWERS.has(nextWord) ? 'his' : 'him'
  }
  return PRONOUN_REVERSE_MAP[lowered] || match
}

function reverseGenderedPronouns(text) {
  const input = String(text || '')
  const replacePronouns = (segment) => segment.replace(PRONOUN_REVERSE_REGEX, (match, ...args) => {
    const replacement = replacementForReversedPronoun(segment, match, args[args.length - 2])
    if (!replacement) return match
    return applyCaseStyle(match, replacement)
  })

  let out = ''
  let lastIndex = 0
  PRONOUN_PROTECTED_REGEX.lastIndex = 0
  let match
  while ((match = PRONOUN_PROTECTED_REGEX.exec(input)) !== null) {
    out += replacePronouns(input.slice(lastIndex, match.index))
    out += match[0]
    lastIndex = match.index + match[0].length
  }
  out += replacePronouns(input.slice(lastIndex))
  return out
}

function previousWord(text, index) {
  const head = text.slice(0, index)
  const m = head.match(/([A-Za-zÀ-ÖØ-öø-ÿ]+)\W*$/)
  return m ? m[1].toLowerCase() : ''
}

function nextWord(text, endIndex) {
  const tail = text.slice(endIndex)
  const m = tail.match(/^\W*([A-Za-zÀ-ÖØ-öø-ÿ]+)/)
  return m ? m[1].toLowerCase() : ''
}

function buildPersonCoreferenceLinks(text, detections) {
  const parsedPeople = detections
    .filter((d) => d.type === 'PERSON')
    .map((d) => {
      const raw = text.slice(d.start, d.end).trim()
      const cleaned = stripPersonTitle(raw).trim()
      const signature = personSignature(cleaned)
      if (!signature) return null
      return {
        raw,
        cleaned,
        canonical: canonicalEntityKey('PERSON', cleaned),
        ...signature,
      }
    })
    .filter(Boolean)

  const fullNames = parsedPeople.filter((entry) => entry.kind === 'full')
  if (fullNames.length === 0) {
    return { additions: [], aliasMap: {} }
  }

  const firstNameMap = new Map()
  const lastNameMap = new Map()
  const initialLastMap = new Map()
  const firstLastInitialMap = new Map()
  const ambiguousFirst = new Set()
  const ambiguousLast = new Set()
  const ambiguousInitialLast = new Set()
  const ambiguousFirstLastInitial = new Set()

  for (const full of fullNames) {
    const firstExisting = firstNameMap.get(full.first)
    if (!firstExisting) {
      firstNameMap.set(full.first, full.canonical)
    } else if (firstExisting !== full.canonical) {
      ambiguousFirst.add(full.first)
    }

    const initialKey = `${full.first[0]}:${full.last}`
    const initialExisting = initialLastMap.get(initialKey)
    if (!initialExisting) {
      initialLastMap.set(initialKey, full.canonical)
    } else if (initialExisting !== full.canonical) {
      ambiguousInitialLast.add(initialKey)
    }

    const firstInitialKey = `${full.first}:${full.last[0]}`
    const firstInitialExisting = firstLastInitialMap.get(firstInitialKey)
    if (!firstInitialExisting) {
      firstLastInitialMap.set(firstInitialKey, full.canonical)
    } else if (firstInitialExisting !== full.canonical) {
      ambiguousFirstLastInitial.add(firstInitialKey)
    }

    const lastExisting = lastNameMap.get(full.last)
    if (!lastExisting) {
      lastNameMap.set(full.last, full.canonical)
    } else if (lastExisting !== full.canonical) {
      ambiguousLast.add(full.last)
    }
  }

  for (const key of ambiguousFirst) firstNameMap.delete(key)
  for (const key of ambiguousLast) lastNameMap.delete(key)
  for (const key of ambiguousInitialLast) initialLastMap.delete(key)
  for (const key of ambiguousFirstLastInitial) firstLastInitialMap.delete(key)

  const aliasMap = {}
  for (const [name, canonical] of firstNameMap.entries()) {
    aliasMap[canonicalEntityKey('PERSON', name)] = canonical
  }
  for (const [name, canonical] of lastNameMap.entries()) {
    aliasMap[canonicalEntityKey('PERSON', name)] = canonical
  }
  for (const person of parsedPeople) {
    let canonical = null
    if (person.kind === 'initial_last') {
      canonical = initialLastMap.get(`${person.firstInitial}:${person.last}`)
    } else if (person.kind === 'first_initial') {
      canonical = firstLastInitialMap.get(`${person.first}:${person.lastInitial}`)
    }
    if (!canonical) continue
    aliasMap[canonicalEntityKey('PERSON', person.cleaned)] = canonical
    aliasMap[canonicalEntityKey('PERSON', person.raw)] = canonical
  }

  const additions = []
  const seenSpans = new Set(detections.filter((d) => d.type === 'PERSON').map((d) => `${d.start}:${d.end}`))

  for (const regex of [new RegExp(`\\b${PERSON_INITIAL_LAST_PATTERN}${PERSON_BOUNDARY_PATTERN}`, 'g'), new RegExp(`\\b${PERSON_FIRST_INITIAL_PATTERN}${PERSON_BOUNDARY_PATTERN}`, 'g')]) {
    regex.lastIndex = 0
    let aliasMatch
    while ((aliasMatch = regex.exec(text)) !== null) {
      const token = aliasMatch[0]
      const start = aliasMatch.index
      const end = start + token.length
      const spanKey = `${start}:${end}`
      if (seenSpans.has(spanKey)) continue
      const signature = personSignature(stripPersonTitle(token).trim())
      if (!signature) continue
      let canonical = null
      if (signature.kind === 'initial_last') {
        canonical = initialLastMap.get(`${signature.firstInitial}:${signature.last}`)
      } else if (signature.kind === 'first_initial') {
        canonical = firstLastInitialMap.get(`${signature.first}:${signature.lastInitial}`)
      }
      if (!canonical) continue
      if (intersectsLocked(start, end, detections)) continue
      if (!isPersonSpanValid(text, start, end, token)) continue
      aliasMap[canonicalEntityKey('PERSON', token)] = canonical
      additions.push({ type: 'PERSON', start, end, score: 0.8 })
      seenSpans.add(spanKey)
    }
  }

  PERSON_SINGLE_NAME_REGEX.lastIndex = 0
  const singleName = PERSON_SINGLE_NAME_REGEX
  let m
  while ((m = singleName.exec(text)) !== null) {
    const token = m[0]
    const lower = token.toLowerCase()
    if (!firstNameMap.has(lower) && !lastNameMap.has(lower)) continue
    if (COMMON_CITY_WORDS.has(lower)) continue
    if (isPersonStopword(token)) continue
    if (ORG_HINT_WORDS.has(lower)) continue
    if (TECH_BLOCK_WORDS.has(lower)) continue
    if (token.length < 3) continue

    const start = m.index
    const end = start + token.length
    if (intersectsLocked(start, end, detections)) continue

    const prev = previousWord(text, start)
    const next = nextWord(text, end)
    if (STREET_SUFFIXES.has(prev) || STREET_SUFFIXES.has(next)) continue
    if (ORG_HINT_WORDS.has(next) || ORG_HINT_WORDS.has(prev)) continue

    additions.push({ type: 'PERSON', start, end, score: 0.79 })
  }

  return { additions, aliasMap }
}

export function anonymizeText(text, entityTypes, options = {}) {
  const tokenStyle = options.tokenStyle === 'emoji' ? 'emoji' : 'standard'
  const reversePronouns = options.reversePronouns === true
  const enabled = new Set(entityTypes.filter((t) => SUPPORTED.has(t)))
  const structured = detectStructuredFields(text, enabled)
  const resolved = []
  const addStage = (detections) => {
    const stage = resolveOverlaps(detections)
    for (const det of stage) {
      if (!overlapsAny(det, resolved)) resolved.push(det)
    }
  }

  // Priority order:
  // Email -> URL -> API Key -> Private Key -> Credit Card -> Government ID -> Bank Account
  // -> IP Address -> Phone -> Address -> Date -> Organisation -> Person -> Location -> Username -> Coordinate -> File Path.
  addStage([
    ...structured.filter((d) => d.type === 'EMAIL'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'EMAIL'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'URL'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'URL'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'API_KEY'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'API_KEY'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'PRIVATE_KEY'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'PRIVATE_KEY'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'CREDIT_CARD'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'CREDIT_CARD'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'GOVERNMENT_ID'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'GOVERNMENT_ID'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'BANK_ACCOUNT'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'BANK_ACCOUNT'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'IP_ADDRESS'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'IP_ADDRESS'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'PHONE'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'PHONE'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'ADDRESS'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'ADDRESS'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'DATE'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'DATE'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'ORG'),
    ...detectHeuristics(text, new Set([...enabled].filter((t) => t === 'ORG')), resolved),
  ])
  addStage(detectPersonFromOrganisationPattern(text, enabled, resolved))
  addStage([
    ...structured.filter((d) => d.type === 'PERSON'),
    ...detectHeuristics(text, new Set([...enabled].filter((t) => t === 'PERSON')), resolved),
  ])
  addStage([
    ...(enabled.has('ADDRESS') ? detectLateLocationCues(text, resolved) : []),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'USERNAME'),
    ...detectUsernames(text, enabled, resolved),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'COORDINATE'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'COORDINATE'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'FILE_PATH'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'FILE_PATH'))),
  ])

  const coref = enabled.has('PERSON') ? buildPersonCoreferenceLinks(text, resolved) : { additions: [], aliasMap: {} }
  addStage(coref.additions)

  resolved.sort((a, b) => a.start - b.start || a.end - b.end)
  const replaced = applyReplacements(text, resolved, tokenStyle, coref.aliasMap)
  const transformedText = reversePronouns && shouldApplyPronounReversal(text)
    ? reverseGenderedPronouns(replaced.anonymized_text)
    : replaced.anonymized_text
  return { ...replaced, anonymized_text: transformedText, cta_visaprep: IMMIGRATION.test(text) }
}
