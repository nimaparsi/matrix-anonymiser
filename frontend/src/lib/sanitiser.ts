import { parsePhoneNumberFromString } from 'libphonenumber-js/min'

export type DetectorKey =
  | 'person'
  | 'organisation'
  | 'email'
  | 'phone'
  | 'date'
  | 'address'
  | 'ip'
  | 'secret'
  | 'id'
  | 'invoice'
  | 'username'

export type TokenType =
  | 'Person'
  | 'Organisation'
  | 'Email'
  | 'Phone'
  | 'Date'
  | 'Address'
  | 'IP'
  | 'Secret'
  | 'ID'
  | 'Invoice'
  | 'Username'

export type SanitiseResult = {
  output: string
  counts: Record<TokenType, number>
  total: number
  detectedLabels: string[]
}

type Detection = {
  type: TokenType
  start: number
  end: number
  score: number
}

type LineInfo = {
  start: number
  end: number
  line: string
}

const TOKEN_TYPES: TokenType[] = [
  'Person',
  'Organisation',
  'Email',
  'Phone',
  'Date',
  'Address',
  'IP',
  'Secret',
  'ID',
  'Invoice',
  'Username',
]

const ENTITY_PRIORITY: Record<TokenType, number> = {
  Secret: 0,
  ID: 1,
  Email: 2,
  IP: 3,
  Phone: 4,
  Address: 5,
  Date: 6,
  Organisation: 7,
  Person: 8,
  Invoice: 9,
  Username: 10,
}

const DAY_MONTH_STOPWORDS = new Set([
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
  'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
  'September', 'October', 'November', 'December',
])
const DAY_MONTH_STOPWORDS_LOWER = new Set([...DAY_MONTH_STOPWORDS].map((word) => word.toLowerCase()))

const STRUCTURED_PERSON_LABELS = new Set([
  'owner',
  'patient',
  'consultant',
  'candidate',
  'name',
  'contact',
  'legal contact',
  'reporter',
  'manager',
  'director',
  'supervisor',
  'employee',
  'applicant',
  'applicant name',
  'employee name',
  'legal contact',
])

const STRUCTURED_ORG_LABELS = new Set([
  'organisation',
  'organization',
  'company',
  'client',
  'employer',
  'current employer',
  'sponsor organisation',
  'sponsor organization',
  'placement company',
])

const UPPERCASE_PERSON_BLOCK_WORDS = new Set([
  'CHECK', 'YOUR', 'INCOME', 'TAX', 'ACCOUNT', 'BACK', 'ENGLISH', 'CYMRAEG',
  'BETA', 'COOKIES', 'ACCESSIBILITY', 'PRIVACY', 'POLICY', 'TERMS', 'CONDITIONS',
  'HELP', 'CONTACT', 'GOVUK', 'CROWN', 'COPYRIGHT', 'DATE', 'TOTAL', 'NATIONAL',
  'INSURANCE', 'PAID', 'TAXABLE', 'HOME', 'MESSAGES', 'PROFILE', 'SETTINGS',
  'SIGN', 'OUT', 'STATEMENT', 'PRINT', 'PAGE', 'SERVICE', 'LICENSE', 'LICENCE',
  'DIGITAL', 'CONSUMER', 'TRENDS', 'GENERATIVE', 'DEVICES', 'NETWORKS', 'VIDEO',
  'ONLINE', 'CONTENTS', 'QUESTION', 'SOURCE', 'WEIGHTED', 'RESPONDENTS',
])

const CONTEXT_GUARD_WORDS = new Set([
  'account', 'messages', 'profile', 'settings', 'sign', 'back', 'english', 'cymraeg',
  'beta', 'cookies', 'accessibility', 'privacy', 'policy', 'terms', 'conditions',
  'help', 'gov', 'copyright', 'print', 'tab', 'income', 'tax', 'national', 'insurance',
  'taxable', 'statement', 'open', 'government', 'licence', 'license',
])

const ORG_SUFFIX = /(Ltd|LTD|Limited|LIMITED|LLC|Inc|INC|Corp|CORP|Corporation|CORPORATION|Group|GROUP|Labs?|LABS?|Research|RESEARCH|Alliance|ALLIANCE|Initiative|INITIATIVE|Systems|SYSTEMS|Solutions|SOLUTIONS|Technologies|TECHNOLOGIES|Tech|TECH|Company|COMPANY)$/
const ORG_HINT_WORDS = new Set([
  'consulting',
  'initiative',
  'university',
  'institute',
  'lab',
  'labs',
  'systems',
  'analytics',
  'research',
  'alliance',
  'group',
  'department',
  'school',
  'faculty',
  'network',
  'foundation',
  'bank',
  'agency',
  'office',
])
const NAME_TOKEN_FRAGMENT = `(?:[A-Z][a-z]+(?:-[A-Z][a-z]+)?|[A-Z]{2,})`
const PERSON_NAME_REGEX = new RegExp(`\\b(?:(?:Dr|Prof|Mr|Mrs|Ms)\\.?\\s+)?(${NAME_TOKEN_FRAGMENT}(?:[ \\t]+${NAME_TOKEN_FRAGMENT}){1,2})\\b`, 'g')
const IPV4_VALUE_REGEX = /^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/
const EXISTING_PLACEHOLDER_REGEX = /^\[(Person|Organisation|Email|Phone|Date|Address|IP|Secret|ID|Invoice|Username)\s+\d+\]$/

export function defaultDetectorState(): Record<DetectorKey, boolean> {
  return {
    person: true,
    organisation: true,
    email: true,
    phone: true,
    date: true,
    address: true,
    ip: true,
    secret: true,
    id: true,
    invoice: true,
    username: true,
  }
}

export function sanitiseText(input: string, detectors: Record<DetectorKey, boolean>): SanitiseResult {
  const text = String(input || '')
  if (!text.trim()) {
    return {
      output: '',
      counts: zeroCounts(),
      total: 0,
      detectedLabels: [],
    }
  }

  const detections: Detection[] = []

  if (detectors.secret) detections.push(...detectSecrets(text))
  if (detectors.id) detections.push(...detectIds(text))
  if (detectors.email) detections.push(...detectEmails(text))
  if (detectors.ip) detections.push(...detectIps(text))
  if (detectors.phone) detections.push(...detectPhones(text))
  if (detectors.address) detections.push(...detectAddresses(text))
  if (detectors.date) detections.push(...detectDates(text))
  if (detectors.organisation) detections.push(...detectOrganisations(text))
  if (detectors.person) detections.push(...detectPeople(text))
  if (detectors.invoice) detections.push(...detectInvoices(text))
  if (detectors.username) detections.push(...detectUsernames(text))

  const accepted = resolveDetections(text, detections)
  const maps = initTokenMaps()
  const counts = zeroCounts()

  const tokenFor = (type: TokenType, raw: string) => {
    const normalized = normalizeKey(raw)
    const existing = maps[type].get(normalized)
    if (existing) return existing
    counts[type] += 1
    const token = `[${type} ${counts[type]}]`
    maps[type].set(normalized, token)
    return token
  }

  const assignedTokens = new Map<string, string>()
  for (const det of accepted) {
    const raw = text.slice(det.start, det.end)
    if (EXISTING_PLACEHOLDER_REGEX.test(raw.trim())) continue
    assignedTokens.set(`${det.type}:${det.start}:${det.end}`, tokenFor(det.type, raw))
  }

  let output = text
  const byEnd = [...accepted].sort((a, b) => b.start - a.start)
  for (const det of byEnd) {
    const raw = output.slice(det.start, det.end)
    if (EXISTING_PLACEHOLDER_REGEX.test(raw.trim())) continue
    const token = assignedTokens.get(`${det.type}:${det.start}:${det.end}`)
    if (!token) continue
    output = `${output.slice(0, det.start)}${token}${output.slice(det.end)}`
  }

  const total = TOKEN_TYPES.reduce((sum, type) => sum + counts[type], 0)
  const detectedLabels = TOKEN_TYPES.filter((type) => counts[type] > 0).map((type) => `${type} x ${counts[type]}`)

  return {
    output,
    counts,
    total,
    detectedLabels,
  }
}

export function splitOutputByTokens(output: string): Array<{ text: string; tokenType?: TokenType }> {
  const tokenRegex = /\[(Person|Organisation|Email|Phone|Date|Address|IP|Secret|ID|Invoice|Username)\s+\d+\]/g
  const result: Array<{ text: string; tokenType?: TokenType }> = []
  let lastIndex = 0

  for (const match of output.matchAll(tokenRegex)) {
    const index = match.index ?? 0
    if (index > lastIndex) {
      result.push({ text: output.slice(lastIndex, index) })
    }
    result.push({ text: match[0], tokenType: match[1] as TokenType })
    lastIndex = index + match[0].length
  }

  if (lastIndex < output.length) {
    result.push({ text: output.slice(lastIndex) })
  }

  return result
}

function detectSecrets(text: string): Detection[] {
  const out: Detection[] = []
  const add = (type: TokenType, start: number, end: number, score = 0.99) => {
    out.push({ type, start, end, score })
  }

  for (const m of text.matchAll(/\b(?:sk_[A-Za-z0-9]{20,}|sk-(?:live|test|proj)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{31,35})\b/g)) {
    add('Secret', m.index ?? 0, (m.index ?? 0) + m[0].length)
  }

  for (const m of text.matchAll(/\bBearer\s+([A-Za-z0-9\-._~+/]+=*)\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add('Secret', start, start + value.length)
  }

  for (const m of text.matchAll(/\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9._-]{8,}\.[A-Za-z0-9._-]{8,}\b/g)) {
    add('Secret', m.index ?? 0, (m.index ?? 0) + m[0].length)
  }

  for (const m of text.matchAll(/\b(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?token|private[_-]?key|client[_-]?secret|db[_-]?password)\b\s*[:=]\s*(["']?)([^\s"'\n]{8,})\1/gi)) {
    const value = m[2]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add('Secret', start, start + value.length)
  }

  for (const m of text.matchAll(/\bssh-(?:rsa|ed25519)\s+[A-Za-z0-9+/=]{32,}(?:\s+\S+)?/g)) {
    add('Secret', m.index ?? 0, (m.index ?? 0) + m[0].length, 0.995)
  }

  for (const m of text.matchAll(/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/g)) {
    add('Secret', m.index ?? 0, (m.index ?? 0) + m[0].length, 1)
  }

  return out
}

function detectIds(text: string): Detection[] {
  const out: Detection[] = []
  const add = (start: number, end: number) => out.push({ type: 'ID', start, end, score: 0.99 })

  for (const m of text.matchAll(/\b(?:NHS\s*(?:no|number|#)\s*[:#-]?\s*)(\d{3}\s?\d{3}\s?\d{4})\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add(start, start + value.length)
  }

  for (const m of text.matchAll(/\b(?:Employer\s+PAYE\s+reference|PAYE\s+reference)\s*[:#-]?\s*([0-9]{3}\/[A-Z0-9]{1,10})\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add(start, start + value.length)
  }

  for (const m of text.matchAll(/\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]\b/g)) {
    add(m.index ?? 0, (m.index ?? 0) + m[0].length)
  }

  for (const m of text.matchAll(/\b\d{3}-\d{2}-\d{4}\b/g)) {
    add(m.index ?? 0, (m.index ?? 0) + m[0].length)
  }

  for (const m of text.matchAll(/\b(?:case|employee|payroll|reference)\s*id\s*[:#-]?\s*([A-Z0-9-]{6,30})\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add(start, start + value.length)
  }

  for (const m of text.matchAll(/\bTax\s+code\s*[:#-]?\s*([A-Z0-9]{3,10})\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add(start, start + value.length)
  }

  for (const m of text.matchAll(/\b(?:ticket(?:\s+reference)?|booking(?:\s+reference)?|order(?:\s+id)?|reservation|reference|pnr)\s*[:#-]?\s*([A-Z0-9-]{8,20})\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add(start, start + value.length)
  }

  return out
}

function detectEmails(text: string): Detection[] {
  return [...text.matchAll(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g)].map((m) => ({
    type: 'Email' as const,
    start: m.index ?? 0,
    end: (m.index ?? 0) + m[0].length,
    score: 0.99,
  }))
}

function detectIps(text: string): Detection[] {
  return [...text.matchAll(/\b(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}\b/g)].map((m) => ({
    type: 'IP' as const,
    start: m.index ?? 0,
    end: (m.index ?? 0) + m[0].length,
    score: 0.99,
  }))
}

function detectPhones(text: string): Detection[] {
  const out: Detection[] = []
  for (const m of text.matchAll(/(?:\+?\d[\d\s().-]{7,}\d)/g)) {
    const start = m.index ?? 0
    const end = start + m[0].length
    const value = m[0].trim()
    if (!isLikelyPhoneValue(value)) continue

    const lineInfo = getLineAt(text, start)
    const digits = value.replace(/\D/g, '')
    const isUkMobileLike = /^0\d{10}$/.test(digits)

    if (isTabularLine(lineInfo.line) && !value.includes('+') && !isUkMobileLike) continue
    if (isBoilerplateLine(lineInfo.line)) continue

    const parsed = parsePhoneNumberFromString(value, 'GB')
    const validByLibrary = Boolean(parsed && (parsed.isValid() || parsed.isPossible()))
    const validByFallback = isUkMobileLike || (value.includes('+') && digits.length >= 10)
    if (!validByLibrary && !validByFallback) continue

    out.push({ type: 'Phone', start, end, score: 0.97 })
  }
  return out
}

function detectDates(text: string): Detection[] {
  const out: Detection[] = []

  for (const m of text.matchAll(/\b(?:DOB|D\.?O\.?B\.?|Date\s+of\s+Birth)\s*:\s*(\d{1,2}[\/.\-]\d{1,2}[\/.\-]\d{2,4})\b/gi)) {
    const value = m[1]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    out.push({ type: 'Date', start, end: start + value.length, score: 0.995 })
  }

  for (const m of text.matchAll(/\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[\/.\-]\d{1,2}[\/.\-]\d{2,4}|\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{2,4})?|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{2,4})\b/gi)) {
    out.push({ type: 'Date', start: m.index ?? 0, end: (m.index ?? 0) + m[0].length, score: 0.94 })
  }

  return out
}

function detectAddresses(text: string): Detection[] {
  const out: Detection[] = []
  const ukPostcodePattern = `[A-Z]{1,2}\\d[A-Z\\d]?\\s*\\d[A-Z]{2}`
  const streetCorePattern = `[A-Z][A-Za-z'’.-]*(?:\\s+[A-Z][A-Za-z'’.-]*){0,5}\\s(?:Street|St|Road|Rd|Lane|Ln|Avenue|Ave|Drive|Dr|Way|Court|Ct|Close|Boulevard|Blvd|Square|Sq|Place|Pl)`
  const cityPattern = `[A-Z][a-z'’-]*(?:\\s+[A-Z][a-z'’-]*){0,3}`
  const labelledAddressRegex = /\b(?:address|registered office|home address|work address|service address|correspondence address|office)\s*:\s*([^\n]+)/gi
  const ukAddressRegex = new RegExp(`\\b\\d{1,5}\\s+${streetCorePattern}(?:,\\s*${cityPattern})?(?:\\s+${ukPostcodePattern})?\\b`, 'g')
  const euAddressRegex = /\b(?:Via|Rue|Calle|Strasse|Strada)\s+[A-Z][A-Za-z'’ -]{2,}(?:,\s*)?\d{1,5}(?:,\s*\d{4,6}\s+[A-Z][A-Za-z'’ -]+)?\b/g

  for (const m of text.matchAll(labelledAddressRegex)) {
    const value = m[1]?.trim()
    if (!value) continue
    const hasStreetIndicator = /\b(?:street|st|road|rd|lane|ln|avenue|ave|drive|dr|way|court|ct|close|boulevard|blvd|square|sq|place|pl|via|rue|calle|strasse|strada)\b/i.test(value)
    const hasUkPostcode = new RegExp(`\\b${ukPostcodePattern}\\b`, 'i').test(value)
    const hasStreetNumber = /\b\d{1,5}\b/.test(value)
    if (!(hasStreetIndicator && hasStreetNumber) && !hasUkPostcode) continue
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    const lineInfo = getLineAt(text, start)
    if (isTabularLine(lineInfo.line)) continue
    out.push({ type: 'Address', start, end: start + value.length, score: 0.985 })
  }

  for (const m of text.matchAll(ukAddressRegex)) {
    const lineInfo = getLineAt(text, m.index ?? 0)
    if (isTabularLine(lineInfo.line)) continue
    out.push({ type: 'Address', start: m.index ?? 0, end: (m.index ?? 0) + m[0].length, score: 0.95 })
  }

  for (const m of text.matchAll(euAddressRegex)) {
    const lineInfo = getLineAt(text, m.index ?? 0)
    if (isTabularLine(lineInfo.line)) continue
    out.push({ type: 'Address', start: m.index ?? 0, end: (m.index ?? 0) + m[0].length, score: 0.93 })
  }

  return out
}

function detectOrganisations(text: string): Detection[] {
  const out: Detection[] = []
  const add = (start: number, end: number, score: number) => out.push({ type: 'Organisation', start, end, score })

  for (const m of text.matchAll(/\b([A-Z][A-Za-z0-9&'.-]*(?:\s+(?:&\s+)?[A-Z][A-Za-z0-9&'.-]*){1,8}\s(?:Ltd|LTD|Limited|LIMITED|LLC|Inc|INC|Corp|CORP|Corporation|CORPORATION|Group|GROUP|Labs?|LABS?|Research|RESEARCH|Alliance|ALLIANCE|Initiative|INITIATIVE|Systems|SYSTEMS|Solutions|SOLUTIONS|Technologies|TECHNOLOGIES|Tech|TECH|Company|COMPANY))\b/g)) {
    add(m.index ?? 0, (m.index ?? 0) + m[1].length, 0.93)
  }

  for (const m of text.matchAll(/\(([^)\n]{2,80})\)/g)) {
    const value = (m[1] || '').trim()
    if (!value || looksLikePersonPhrase(value) || !isLikelyOrganisationPhrase(value)) continue
    const start = (m.index ?? 0) + m[0].indexOf(value)
    add(start, start + value.length, 0.91)
  }

  for (const m of text.matchAll(/\b(?:from|at|of)\s+([A-Z][A-Za-z0-9&'.-]*(?:\s+[A-Z][A-Za-z0-9&'.-]*){0,5})\b/g)) {
    const value = (m[1] || '').trim()
    if (!value || looksLikePersonPhrase(value) || !isLikelyOrganisationPhrase(value)) continue
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    add(start, start + value.length, 0.9)
  }

  const lines = text.split('\n')
  let offset = 0
  for (const line of lines) {
    const idx = line.indexOf(':')
    if (idx >= 0) {
      const label = line.slice(0, idx).trim().toLowerCase()
      const value = line.slice(idx + 1).trim()
      if (value && STRUCTURED_ORG_LABELS.has(label) && !EXISTING_PLACEHOLDER_REGEX.test(value)) {
        const start = offset + idx + 1 + (line.slice(idx + 1).length - line.slice(idx + 1).trimStart().length)
        add(start, start + value.length, 0.98)
      }
    }
    offset += line.length + 1
  }

  return out
}

function detectPeople(text: string): Detection[] {
  const out: Detection[] = []
  const lines = text.split('\n')
  let offset = 0

  for (const line of lines) {
    const trimmed = line.trim()
    const idx = line.indexOf(':')

    if (idx >= 0) {
      const label = line.slice(0, idx).trim().toLowerCase()
      const value = line.slice(idx + 1).trim()
      if (value && STRUCTURED_PERSON_LABELS.has(label) && !EXISTING_PLACEHOLDER_REGEX.test(value)) {
        const match = value.match(new RegExp(`(?:(?:Dr|Prof|Mr|Mrs|Ms)\\.?\\s+)?(${NAME_TOKEN_FRAGMENT}(?:[ \\t]+${NAME_TOKEN_FRAGMENT}){1,2})`))
        if (match) {
          const parts = (match[1] || '').split(/[ \t]+/).filter(Boolean)
          const hasBlocked = parts.some((part) => DAY_MONTH_STOPWORDS_LOWER.has(part.toLowerCase()))
          if (!hasBlocked && !ORG_SUFFIX.test(match[0])) {
            const startInValue = value.indexOf(match[0])
            const start = offset + idx + 1 + (line.slice(idx + 1).length - line.slice(idx + 1).trimStart().length) + startInValue
            out.push({ type: 'Person', start, end: start + match[0].length, score: 0.98 })
          }
        }
      }
    }

    if (/^[A-Z][A-Z' -]{4,}$/.test(trimmed)) {
      const parts = trimmed.split(/\s+/).filter(Boolean)
      const normalized = parts.map((word) => word.replace(/[^A-Z]/g, ''))
      if (
        parts.length >= 2 &&
        parts.length <= 4 &&
        !normalized.some((word) => UPPERCASE_PERSON_BLOCK_WORDS.has(word)) &&
        !isBoilerplateLine(trimmed) &&
        !isTabularLine(trimmed)
      ) {
        const start = offset + line.indexOf(trimmed)
        out.push({ type: 'Person', start, end: start + trimmed.length, score: 0.9 })
      }
    }

    offset += line.length + 1
  }

  for (const m of text.matchAll(PERSON_NAME_REGEX)) {
    const full = m[0] || ''
    const candidate = m[1] || ''
    if (!candidate) continue
    const start = (m.index ?? 0) + full.lastIndexOf(candidate)
    const end = start + candidate.length
    const lineInfo = getLineAt(text, start)
    if (isTabularLine(lineInfo.line) || isBoilerplateLine(lineInfo.line)) continue
    if (!hasPersonLikeContext(text, start, end)) continue
    if (looksLikePersonStopPhrase(candidate) || ORG_SUFFIX.test(candidate)) continue
    out.push({ type: 'Person', start, end, score: 0.9 })
  }

  return out
}

function detectInvoices(text: string): Detection[] {
  const out: Detection[] = []
  for (const m of text.matchAll(/\b(?:INV-[A-Z0-9]{3,}(?!\d)|invoice\s*#\s*[A-Z0-9-]{2,}(?!\d)|order\s*(?:id|#)?\s*[:#-]?\s*[A-Z0-9-]{6,}|booking\s*(?:id|ref(?:erence)?|#)?\s*[:#-]?\s*[A-Z0-9-]{6,}|reference\s*(?:id|#)?\s*[:#-]?\s*[A-Z0-9-]{6,})/gi)) {
    out.push({ type: 'Invoice', start: m.index ?? 0, end: (m.index ?? 0) + m[0].length, score: 0.96 })
  }
  return out
}

function detectUsernames(text: string): Detection[] {
  const out: Detection[] = []

  for (const m of text.matchAll(/\b((?:github|slack)\s+user(?:name)?\s*[:=]\s*)(@?[a-zA-Z][a-zA-Z0-9._-]{2,})\b/gi)) {
    const value = m[2]
    const start = (m.index ?? 0) + m[0].lastIndexOf(value)
    out.push({ type: 'Username', start, end: start + value.length, score: 0.97 })
  }

  for (const m of text.matchAll(/\B@([a-zA-Z][a-zA-Z0-9._-]{2,})\b/g)) {
    const start = (m.index ?? 0)
    out.push({ type: 'Username', start, end: start + m[0].length, score: 0.95 })
  }

  return out
}

function resolveDetections(text: string, detections: Detection[]): Detection[] {
  const uniq = new Map<string, Detection>()
  for (const d of detections) {
    if (d.start >= d.end) continue
    const raw = text.slice(d.start, d.end)
    if (EXISTING_PLACEHOLDER_REGEX.test(raw.trim())) continue
    const key = `${d.type}:${d.start}:${d.end}`
    const prev = uniq.get(key)
    if (!prev || prev.score < d.score) uniq.set(key, d)
  }

  const ranked = [...uniq.values()].sort((a, b) => {
    const prio = (ENTITY_PRIORITY[a.type] ?? 99) - (ENTITY_PRIORITY[b.type] ?? 99)
    if (prio !== 0) return prio
    const len = (b.end - b.start) - (a.end - a.start)
    if (len !== 0) return len
    return a.start - b.start
  })

  const selected: Detection[] = []
  for (const cand of ranked) {
    if (selected.some((d) => rangesOverlap(d.start, d.end, cand.start, cand.end))) continue
    selected.push(cand)
  }

  return selected.sort((a, b) => a.start - b.start)
}

function rangesOverlap(aStart: number, aEnd: number, bStart: number, bEnd: number) {
  return !(aEnd <= bStart || bEnd <= aStart)
}

function getLineAt(text: string, index: number): LineInfo {
  const safe = Math.max(0, Math.min(index, Math.max(text.length - 1, 0)))
  let start = safe
  let end = safe
  while (start > 0 && text[start - 1] !== '\n') start -= 1
  while (end < text.length && text[end] !== '\n') end += 1
  return { start, end, line: text.slice(start, end) }
}

function isTabularLine(line: string) {
  const normalized = String(line || '').trim()
  if (!normalized) return false
  if (normalized.includes('\t')) return true
  const numericTokens = normalized.match(/\d[\d,]*(?:\.\d+)?/g) || []
  const separatedColumns = normalized.split(/\s{2,}/).length
  return numericTokens.length >= 3 && separatedColumns >= 2
}

function isBoilerplateLine(line: string) {
  const words = String(line || '')
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(Boolean)
  if (words.length === 0) return false
  const hits = words.filter((w) => CONTEXT_GUARD_WORDS.has(w)).length
  return hits >= 3 || (hits >= 2 && hits / words.length >= 0.35)
}

function isLikelyPhoneValue(value: string) {
  const candidate = String(value || '').trim()
  if (!candidate) return false
  if (IPV4_VALUE_REGEX.test(candidate)) return false
  if (candidate.includes(',') || candidate.includes('%') || candidate.includes('£')) return false
  if (/^(?:\d{4}\s+){1,}\d{4}$/.test(candidate)) return false

  const digits = candidate.replace(/\D/g, '')
  if (digits.length < 10 || digits.length > 15) return false

  const hasIntlOrParen = candidate.includes('+') || candidate.includes('(') || candidate.includes(')')
  const separatorCount = (candidate.match(/[\s.-]/g) || []).length
  const isUkMobileLike = /^0\d{10}$/.test(digits)
  if (!hasIntlOrParen && separatorCount < 2 && !isUkMobileLike) return false

  const groups = candidate.split(/[\s.-]+/).filter(Boolean)
  if (groups.length >= 5 && groups.every((g) => /^\d{1,2}$/.test(g))) return false
  if (!hasIntlOrParen && groups.length >= 4 && groups.every((g) => /^\d{1,4}$/.test(g))) return false
  return true
}

function looksLikePersonStopPhrase(value: string) {
  const words = String(value || '')
    .split(/\s+/)
    .map((word) => word.replace(/[^A-Za-z]/g, '').toLowerCase())
    .filter(Boolean)
  if (words.length < 2 || words.length > 3) return true
  if (words.some((word) => DAY_MONTH_STOPWORDS_LOWER.has(word))) return true
  if (words.some((word) => CONTEXT_GUARD_WORDS.has(word))) return true
  return false
}

function hasPersonLikeContext(text: string, start: number, end: number) {
  const before = text.slice(Math.max(0, start - 36), start).toLowerCase()
  const after = text.slice(end, Math.min(text.length, end + 36)).toLowerCase()

  if (/(?:^|[\s,(])(?:dr|prof|mr|mrs|ms)\.?\s*$/.test(before)) return true
  if (/(?:owner|candidate|manager|director|reporter|supervisor|assistant|contact|dear|hi|hello|from|by|with)\s*[:,-]?\s*$/.test(before)) return true
  if (/(?:best|kind regards|regards|thanks)[\s,:-]*$/i.test(before)) return true
  if (/^\s*(?:,|\band\b|\bconfirmed\b|\bsaid\b|\bjoined\b|\bemailed\b|\bcalled\b|\bwill\b|\bis\b|\bwas\b|\bfrom\b|\bat\b|\bof\b)/.test(after)) return true
  return false
}

function looksLikePersonPhrase(value: string) {
  const words = String(value || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
  if (words.length < 2 || words.length > 3) return false
  return words.every((word) => /^[A-Z][a-z]+(?:-[A-Z][a-z]+)?$/.test(word))
}

function isLikelyOrganisationPhrase(value: string) {
  const cleaned = String(value || '').trim()
  if (!cleaned || EXISTING_PLACEHOLDER_REGEX.test(cleaned)) return false
  if (/^\d+$/.test(cleaned)) return false
  if (/^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$/.test(cleaned) && looksLikePersonPhrase(cleaned)) return false

  const words = cleaned
    .split(/\s+/)
    .map((word) => word.replace(/[^A-Za-z0-9]/g, ''))
    .filter(Boolean)
  if (words.length === 0 || words.length > 6) return false
  const lower = words.map((word) => word.toLowerCase())
  const hasHint = lower.some((word) => ORG_HINT_WORDS.has(word))
  const hasSuffix = ORG_SUFFIX.test(words[words.length - 1] || '')
  const isCamelSingle = words.length === 1 && /[a-z][A-Z]/.test(words[0])
  return hasHint || hasSuffix || isCamelSingle
}

function normalizeKey(value: string) {
  return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ')
}

function initTokenMaps() {
  return {
    Person: new Map<string, string>(),
    Organisation: new Map<string, string>(),
    Email: new Map<string, string>(),
    Phone: new Map<string, string>(),
    Date: new Map<string, string>(),
    Address: new Map<string, string>(),
    IP: new Map<string, string>(),
    Secret: new Map<string, string>(),
    ID: new Map<string, string>(),
    Invoice: new Map<string, string>(),
    Username: new Map<string, string>(),
  }
}

function zeroCounts(): Record<TokenType, number> {
  return {
    Person: 0,
    Organisation: 0,
    Email: 0,
    Phone: 0,
    Date: 0,
    Address: 0,
    IP: 0,
    Secret: 0,
    ID: 0,
    Invoice: 0,
    Username: 0,
  }
}

export const TOOL_EXAMPLE_INPUT = `Subject: Security Incident
Report - Ticket #8821
From: sarah.connor@cyberdyne-tech.com
Priority: High

We detected unauthorized access attempts on server 192.168.1.105.
The user was identified as 'j_reese_84'.
Please contact admin at +1-555-0199 for more details.
API Key used: sk_live_51MzhZ6L2nQ7vB0P3x...`
