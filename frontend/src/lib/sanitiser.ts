export type DetectorKey =
  | 'person'
  | 'organisation'
  | 'email'
  | 'phone'
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

const ORG_SUFFIX = /(Ltd|Limited|LLC|Inc|Corp|Corporation|Group|Labs?|Research|Alliance|Initiative|Systems|Solutions|Technologies|Tech|Company)$/i
const IPV4_VALUE_REGEX = /^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/

const TOKEN_TYPES: TokenType[] = [
  'Person',
  'Organisation',
  'Email',
  'Phone',
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
    if (IPV4_VALUE_REGEX.test(match.trim())) return match
    return tokenFor('Phone', match)
  })

  replaceIf(detectors.invoice, /\b(?:INV-\d{3,}|invoice\s*#\s*\d{2,})\b/gi, (match) => tokenFor('Invoice', match))

  replaceIf(
    detectors.address,
    /\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,4}\s(?:Street|St|Road|Rd|Lane|Ln|Avenue|Ave|Drive|Dr|Way|Court|Ct|Close|Boulevard|Blvd)(?:,\s*[A-Za-z][A-Za-z' -]*?)?(?:\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2})?\b/g,
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
    /\b(?:from|at|with|for)\s+([A-Z][A-Za-z0-9&'.-]*(?:\s+[A-Z][A-Za-z0-9&'.-]*){0,3})\b/g,
    (full, orgName: string) => {
      if (orgName.startsWith('[')) return full
      if (isLikelyPerson(orgName) && !ORG_SUFFIX.test(orgName)) return full
      return full.replace(orgName, tokenFor('Organisation', orgName))
    },
  )

  replaceIf(
    detectors.organisation,
    /\b([A-Z][A-Za-z0-9&'.-]*(?:\s+[A-Z][A-Za-z0-9&'.-]*){1,3}\s(?:Ltd|Limited|LLC|Inc|Corp|Corporation|Group|Labs?|Research|Alliance|Initiative|Systems|Solutions|Technologies|Tech|Company))\b/g,
    (match) => {
      if (match.startsWith('[')) return match
      return tokenFor('Organisation', match)
    },
  )

  replaceIf(detectors.person, /\b(?:(?:Dr|Prof|Mr|Mrs|Ms)\.?\s+)?([A-Z][a-z]+(?:-[A-Z][a-z]+)?[ \t]+[A-Z][a-z]+)\b/g, (match, name: string) => {
    if (match.startsWith('[')) return match

    const [firstWord, secondWord] = name.split(/[ \t]+/)
    if (DAY_MONTH_STOPWORDS.has(firstWord) || DAY_MONTH_STOPWORDS.has(secondWord)) return match
    if (ORG_SUFFIX.test(match)) return match

    return tokenFor('Person', match)
  })

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
  const tokenRegex = /\[(Person|Organisation|Email|Phone|Address|IP|Secret|Invoice|Username)\s+\d+\]/g
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
    Address: 0,
    IP: 0,
    Secret: 0,
    Invoice: 0,
    Username: 0,
  }
}

function isLikelyPerson(value: string) {
  return /^[A-Z][a-z]+\s+[A-Z][a-z]+$/.test(value)
}

export const TOOL_EXAMPLE_INPUT = `Subject: Security Incident
Report - Ticket #8821
From: sarah.connor@cyberdyne-tech.com
Priority: High

We detected unauthorized access attempts on server 192.168.1.105.
The user was identified as 'j_reese_84'.
Please contact admin at +1-555-0199 for more details.
API Key used: sk_live_51MzhZ6L2nQ7vB0P3x...`
