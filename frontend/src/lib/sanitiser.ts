export type DetectorKey =
  | 'person'
  | 'organisation'
  | 'email'
  | 'phone'
  | 'date'
  | 'address'
  | 'ip'
  | 'secret'
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
  | 'Invoice'
  | 'Username'

export type SanitiseResult = {
  output: string
  counts: Record<TokenType, number>
  total: number
  detectedLabels: string[]
}

const DAY_MONTH_STOPWORDS = new Set([
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
])
const STREET_PLACE_WORDS = new Set([
  'Street',
  'St',
  'Road',
  'Rd',
  'Lane',
  'Ln',
  'Avenue',
  'Ave',
  'Drive',
  'Dr',
  'Way',
  'Court',
  'Ct',
  'Close',
  'Boulevard',
  'Blvd',
  'Square',
  'Sq',
  'Place',
  'Pl',
])

const ORG_SUFFIX = /(Ltd|Limited|LLC|Inc|Corp|Corporation|Group|Labs?|Research|Alliance|Initiative|Systems|Solutions|Technologies|Tech|Company)$/i
const IPV4_VALUE_REGEX = /^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/
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
])
const STRUCTURED_ORG_LABELS = new Set(['organisation', 'organization', 'company', 'client', 'employer', 'current employer'])
const UPPERCASE_PERSON_BLOCK_WORDS = new Set([
  'CHECK',
  'YOUR',
  'INCOME',
  'TAX',
  'ACCOUNT',
  'BACK',
  'ENGLISH',
  'CYMRAEG',
  'BETA',
  'COOKIES',
  'ACCESSIBILITY',
  'PRIVACY',
  'POLICY',
  'TERMS',
  'CONDITIONS',
  'HELP',
  'CONTACT',
  'GOVUK',
  'CROWN',
  'COPYRIGHT',
  'DATE',
  'TOTAL',
  'NATIONAL',
  'INSURANCE',
  'PAID',
  'TAXABLE',
  'HOME',
  'MESSAGES',
  'PROFILE',
  'SETTINGS',
  'SIGN',
  'OUT',
])

const TOKEN_TYPES: TokenType[] = [
  'Person',
  'Organisation',
  'Email',
  'Phone',
  'Date',
  'Address',
  'IP',
  'Secret',
  'Invoice',
  'Username',
]

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
    invoice: true,
    username: true,
  }
}

export function sanitiseText(input: string, detectors: Record<DetectorKey, boolean>): SanitiseResult {
  if (!input.trim()) {
    return {
      output: '',
      counts: zeroCounts(),
      total: 0,
      detectedLabels: [],
    }
  }

  const tokenMaps = initTokenMaps()
  const counts = zeroCounts()

  const tokenFor = (type: TokenType, raw: string) => {
    const normalised = raw.trim().toLowerCase()
    const existing = tokenMaps[type].get(normalised)
    if (existing) return existing

    counts[type] += 1
    const token = `[${type} ${counts[type]}]`
    tokenMaps[type].set(normalised, token)
    return token
  }

  let output = input

  const replaceIf = (enabled: boolean, regex: RegExp, replacer: (...args: any[]) => string) => {
    if (!enabled) return
    output = output.replace(regex, replacer)
  }

  replaceIf(
    detectors.secret,
    /\b(?:sk_(?:live|test)_[A-Za-z0-9]{12,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|ssh-(?:rsa|ed25519)\s+[A-Za-z0-9+/=]{32,}(?:\s+\S+)?|(?:api[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*[A-Za-z0-9._-]{12,})\b/gi,
    (match) => tokenFor('Secret', match),
  )

  replaceIf(
    detectors.secret,
    /\b(?:NHS\s*(?:no|number|#)\s*:\s*)(\d{3}\s?\d{3}\s?\d{4})\b/gi,
    (full, nhsNo: string) => full.replace(nhsNo, tokenFor('Secret', nhsNo)),
  )

  replaceIf(detectors.email, /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, (match) => tokenFor('Email', match))

  replaceIf(detectors.ip, /\b(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}\b/g, (match) => tokenFor('IP', match))

  replaceIf(detectors.phone, /(?:\+?\d[\d\s().-]{7,}\d)/g, (match) => {
    if (!isLikelyPhoneValue(match)) return match
    return tokenFor('Phone', match)
  })

  replaceIf(
    detectors.date,
    /\b(?:DOB|D\.?O\.?B\.?|Date\s+of\s+Birth)\s*:\s*(\d{1,2}[\/.-]\d{1,2}[\/.-]\d{2,4})\b/gi,
    (full, dateValue: string) => full.replace(dateValue, tokenFor('Date', dateValue)),
  )

  replaceIf(
    detectors.date,
    /\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[\/.-]\d{1,2}[\/.-]\d{2,4}|\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{2,4})?|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{2,4})\b/gi,
    (match) => tokenFor('Date', match),
  )

  replaceIf(detectors.invoice, /\b(?:INV-\d{3,}(?!\d)|invoice\s*#\s*\d{2,}(?!\d))/gi, (match) => tokenFor('Invoice', match))

  replaceIf(
    detectors.address,
    /\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,4}\s(?:Street|St|Road|Rd|Lane|Ln|Avenue|Ave|Drive|Dr|Way|Court|Ct|Close|Boulevard|Blvd|Square|Sq)(?:,\s*[A-Za-z][A-Za-z0-9' -]*)?(?!\d)/g,
    (match) => tokenFor('Address', match),
  )

  replaceIf(
    detectors.username,
    /\b((?:github|slack)\s+user(?:name)?\s*[:=]\s*)(@?[a-zA-Z][a-zA-Z0-9._-]{2,})\b/gi,
    (_full, prefix: string, handle: string) => `${prefix}${tokenFor('Username', handle)}`,
  )

  replaceIf(
    detectors.username,
    /\b(user(?:name)?\s*[:=]\s*['"]?)([a-zA-Z][a-zA-Z0-9._-]{2,})(['"]?)\b/gi,
    (_full, prefix: string, handle: string, suffix: string) => `${prefix}${tokenFor('Username', handle)}${suffix}`,
  )

  replaceIf(
    detectors.organisation,
    /\b([A-Z][A-Za-z0-9&'.-]*(?:\s+(?:&\s+)?[A-Z][A-Za-z0-9&'.-]*){1,5}\s(?:Ltd|LTD|Limited|LIMITED|LLC|Inc|INC|Corp|CORP|Corporation|CORPORATION|Group|GROUP|Labs?|LABS?|Research|RESEARCH|Alliance|ALLIANCE|Initiative|INITIATIVE|Systems|SYSTEMS|Solutions|SOLUTIONS|Technologies|TECHNOLOGIES|Tech|TECH|Company|COMPANY))\b/g,
    (match) => {
      if (match.startsWith('[')) return match
      return tokenFor('Organisation', match)
    },
  )

  output = output
    .split('\n')
    .map((line) => {
      const trimmed = line.trim()
      const idx = line.indexOf(':')
      if (idx >= 0) {
        const label = line.slice(0, idx).trim().toLowerCase()
        const value = line.slice(idx + 1).trim()
        if (value && !value.startsWith('[')) {
          if (detectors.organisation && STRUCTURED_ORG_LABELS.has(label)) {
            return `${line.slice(0, idx + 1)} ${tokenFor('Organisation', value)}`
          }
          if (detectors.person && STRUCTURED_PERSON_LABELS.has(label)) {
            const m = value.match(/(?:(?:Dr|Prof|Mr|Mrs|Ms)\.?\s+)?([A-Z][a-z]+(?:-[A-Z][a-z]+)?[ \t]+[A-Z][a-z]+)/)
            if (m) return `${line.slice(0, idx + 1)} ${value.replace(m[0], tokenFor('Person', m[0]))}`
          }
        }
      }

      if (detectors.person && /^[A-Z][A-Z' -]{4,}$/.test(trimmed)) {
        const parts = trimmed.split(/\s+/).filter(Boolean)
        const normalized = parts.map((word) => word.replace(/[^A-Z]/g, ''))
        if (normalized.some((word) => UPPERCASE_PERSON_BLOCK_WORDS.has(word))) return line
        if (parts.length >= 2 && parts.length <= 4) {
          return line.replace(trimmed, tokenFor('Person', trimmed))
        }
      }

      return line
    })
    .join('\n')

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
  const tokenRegex = /\[(Person|Organisation|Email|Phone|Date|Address|IP|Secret|Invoice|Username)\s+\d+\]/g
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
    Invoice: 0,
    Username: 0,
  }
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
  const compactDigits = candidate.replace(/\D/g, '')
  const isUkMobileLike = /^0\d{10}$/.test(compactDigits)
  if (!hasIntlOrParen && separatorCount < 2 && !isUkMobileLike) return false
  const groups = candidate.split(/[\s.-]+/).filter(Boolean)
  if (groups.length >= 5 && groups.every((g) => /^\d{1,2}$/.test(g))) return false
  if (!hasIntlOrParen && groups.length >= 4 && groups.every((g) => /^\d{1,4}$/.test(g))) return false
  return true
}

export const TOOL_EXAMPLE_INPUT = `Subject: Security Incident
Report - Ticket #8821
From: sarah.connor@cyberdyne-tech.com
Priority: High

We detected unauthorized access attempts on server 192.168.1.105.
The user was identified as 'j_reese_84'.
Please contact admin at +1-555-0199 for more details.
API Key used: sk_live_51MzhZ6L2nQ7vB0P3x...`
