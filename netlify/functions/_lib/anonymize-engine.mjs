const SUPPORTED = new Set(['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL'])
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
  'school', 'faculty', 'consulting', 'analytics', 'systems',
  'energy', 'urban', 'coastal', 'ecologic', 'future', 'horizon', 'growth',
  'teams', 'drive', 'jira', 'salesforce', 'nightfall', 'atlassian', 'microsoft', 'google', 'visaprep',
])
const ORG_SUFFIX_WORDS = new Set([
  'ltd', 'limited', 'inc', 'llc', 'consulting', 'initiative', 'university', 'lab', 'labs',
  'research', 'alliance', 'group', 'institute', 'network', 'foundation', 'agency',
  'council', 'bank', 'office', 'department', 'school', 'faculty', 'systems',
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
const FIELD_LABEL_WORDS = new Set(['person', 'email', 'phone', 'address', 'organisation', 'organization', 'date', 'url', 'website', 'web'])
const DISCOURSE_WORDS = new Set(['later', 'then', 'next', 'afterward', 'afterwards', 'meanwhile'])
const COMMON_CITY_WORDS = new Set([
  'london', 'manchester', 'birmingham', 'leeds', 'liverpool', 'bristol', 'sheffield',
  'cambridge', 'oxford', 'brighton', 'new', 'york', 'paris', 'berlin', 'tokyo',
])
const NON_PERSON_SINGLE_BLOCK = new Set([
  'apple', 'google', 'microsoft', 'openai', 'amazon', 'meta',
  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
])
const NAME_TOKEN_PATTERN = '[A-Z][a-z]{1,}(?:-[A-Z][a-z]{1,})*'
const INITIAL_TOKEN_PATTERN = '[A-Z]\\.'
const INITIAL_TOKEN_REGEX = /^[A-Z]\.$/
const INITIAL_NAME_PATTERN = `${INITIAL_TOKEN_PATTERN}\\s+${NAME_TOKEN_PATTERN}`
const PERSON_CONTEXT_NAME_PATTERN = `${NAME_TOKEN_PATTERN}(?:\\s+${NAME_TOKEN_PATTERN})?`
const NAME_TOKEN_REGEX = new RegExp(`^${NAME_TOKEN_PATTERN}$`)
const PERSON_TITLE_REGEX = /^(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+/
const PERSON_FULL_NAME_REGEX = new RegExp(`\\b(?:Mr|Mrs|Ms|Dr|Prof)\\.?\\s+(?:${PERSON_CONTEXT_NAME_PATTERN}|${INITIAL_NAME_PATTERN})\\b|\\b${NAME_TOKEN_PATTERN}\\s+${NAME_TOKEN_PATTERN}\\b|\\b${INITIAL_NAME_PATTERN}\\b`, 'g')
const PERSON_SINGLE_NAME_REGEX = new RegExp(`\\b${NAME_TOKEN_PATTERN}\\b`, 'g')

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

function isLikelyPhoneValue(value) {
  const digits = String(value || '').replace(/\D/g, '')
  return digits.length >= 8 && digits.length <= 15 && (digits.length >= 10 || String(value || '').includes('+') || /[\s.-]/.test(String(value || '')))
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
  if (trimmed.length > 120) return false
  if (/[.!?]/.test(trimmed)) return false
  const words = trimmed.split(/\s+/).filter(Boolean)
  if (words.length < 2 || words.length > 10) return false
  const titleLike = words.filter((w) => /^[A-Z][A-Za-z0-9&'+-]*$/.test(w)).length
  const ratio = titleLike / words.length
  const hasUiSymbol = /[&|/]/.test(trimmed)
  const hasTech = words.some((w) => TECH_BLOCK_WORDS.has(w.toLowerCase()))
  return ratio >= 0.9 || (ratio >= 0.7 && (hasUiSymbol || hasTech))
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
  if (parts.length !== 2) return false
  const [first, last] = parts
  if (!(NAME_TOKEN_REGEX.test(first) || INITIAL_TOKEN_REGEX.test(first)) || !NAME_TOKEN_REGEX.test(last)) return false
  const firstLower = first.toLowerCase()
  const lastLower = last.toLowerCase()
  if (isPersonStopword(first) || isPersonStopword(last)) return false
  if (CTA_ACTION_WORDS.has(firstLower)) return false
  if (DISCOURSE_WORDS.has(firstLower) || DISCOURSE_WORDS.has(lastLower)) return false
  if (TECH_BLOCK_WORDS.has(firstLower) || TECH_BLOCK_WORDS.has(lastLower)) return false
  if (ORG_HINT_WORDS.has(firstLower) || ORG_HINT_WORDS.has(lastLower)) return false
  if (ORG_SUFFIX_WORDS.has(firstLower) || ORG_SUFFIX_WORDS.has(lastLower)) return false
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

const REGEX = {
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  PHONE: /(?:\+\d{1,3}(?:[\s.-]?\(?\d{1,4}\)?){1,4}|\b\(?\d{2,4}\)?(?:[\s.-]\d{2,4}){1,3}\b|\b\d{10,15}\b)/g,
  URL: /https?:\/\/[^\s]+/gi,
  UK_REF: /\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b/gi,
  PASSPORT: /\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b/g,
  DATE: /\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}\s?(?:am|pm)?|\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:,?\s+\d{2,4})?|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{2,4})?)\b/gi,
  UK_POSTCODE: /\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/gi,
  ADDRESS_UK_FULL: /\b\d{1,5}[A-Za-z]?\s+(?:[A-Z][A-Za-z' -]*(?:-[A-Z][A-Za-z' -]*)*\s+){0,4}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd)\b(?:,\s*[A-Z][A-Za-z' -]{1,40}\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b|,\s*[A-Z][A-Za-z' -]{1,40}\b)?/g,
  ADDRESS_VIA: /\bVia\s+[A-Z][A-Za-z' -]*(?:-[A-Z][A-Za-z' -]*)*(?:\s+[A-Z][A-Za-z' -]*(?:-[A-Z][A-Za-z' -]*)*){0,2}\b/g,
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
  PHONE: { label: 'Phone', emoji: '📞' },
  ADDRESS: { label: 'Location', emoji: '📍' },
  ORG: { label: 'Organisation', emoji: '🏢' },
  DATE: { label: 'Date', emoji: '📅' },
  URL: { label: 'Web Address', emoji: '🔗' },
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
  add('PHONE', REGEX.PHONE)
  add('DATE', REGEX.DATE)

  if (enabled.has('ADDRESS')) {
    // Prefer full address spans first to avoid partial leaks.
    REGEX.ADDRESS_UK_FULL.lastIndex = 0
    let m
    while ((m = REGEX.ADDRESS_UK_FULL.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.995 })
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

    for (const key of ['UK_REF', 'PASSPORT']) {
      REGEX[key].lastIndex = 0
      while ((m = REGEX[key].exec(text)) !== null) {
        out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.95 })
      }
    }
  }

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
  }

  for (const line of lines) {
    const m = line.match(/^\s*([A-Za-z]+)\s*(?::|->|→)\s*(.+?)\s*$/)
    if (m) {
      const label = m[1].toLowerCase()
      const mapped = labelMap[label]
      if (mapped && enabled.has(mapped)) {
        const value = m[2]
        const valueStartInLine = line.indexOf(value)
        if (valueStartInLine >= 0) {
          if (mapped === 'PERSON') {
            const personInList = new RegExp(`(?:Mr|Mrs|Ms|Dr|Prof)\\.?\\s+(?:${PERSON_CONTEXT_NAME_PATTERN}|${INITIAL_NAME_PATTERN})|${PERSON_CONTEXT_NAME_PATTERN}|${INITIAL_NAME_PATTERN}`, 'g')
            let pm
            while ((pm = personInList.exec(value)) !== null) {
              const token = pm[0]
              const start = offset + valueStartInLine + pm.index
              const end = start + token.length
              if (!isPersonSpanValid(text, start, end, token)) continue
              out.push({ type: mapped, start, end, score: 0.995 })
            }
          } else {
            out.push({
              type: mapped,
              start: offset + valueStartInLine,
              end: offset + valueStartInLine + value.length,
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
  if (type === 'EMAIL') {
    const m = segment.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/)
    return m ? m[0] : ''
  }
  if (type === 'URL') {
    const m = segment.match(/https?:\/\/[^\s,;]+/i)
    return m ? m[0] : ''
  }
  if (type === 'PHONE') {
    const m = segment.match(/\+?\d[\d\s().-]{6,}\d/)
    return m ? m[0].trim() : ''
  }
  if (type === 'DATE') {
    const m = segment.match(REGEX.DATE)
    return m ? m[0] : ''
  }
  if (type === 'PERSON') {
    PERSON_FULL_NAME_REGEX.lastIndex = 0
    const m = PERSON_FULL_NAME_REGEX.exec(segment)
    return m ? m[0] : ''
  }
  if (type === 'ORG') {
    const stop = segment.search(/(?:,\s*(?:Date|Person|Email|Phone|Address|Organisation|Organization)\b|[.;]\s)/)
    return (stop >= 0 ? segment.slice(0, stop) : segment).trim()
  }
  if (type === 'ADDRESS') {
    const stop = segment.search(/(?:,\s*(?:Organisation|Organization|Date|Person|Email|Phone|Address)\b|[.;]\s)/)
    return (stop >= 0 ? segment.slice(0, stop) : segment).trim()
  }
  return segment
}

function detectHeuristics(text, enabled, locked = []) {
  const out = []
  if (enabled.has('PERSON')) {
    // Narrative single-name cues: "named Liam", "called Sarah".
    const namedOrCalled = new RegExp(`\\b(named|called)\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\b`, 'gi')
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
    const roleName = new RegExp(`\\b(?:analyst|engineer|developer|researcher|assistant|manager|consultant|officer|intern)\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\b`, 'gi')
    while ((m = roleName.exec(text)) !== null) {
      const name = m[1]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.83 })
    }

    // Clause subject cue: "that Sarah joined...", "that Liam wrote...".
    const thatSubject = new RegExp(`\\bthat\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\s+(is|was|has|had|works|worked|lives|lived|moved|joined|arrived|said|wrote)\\b`, 'g')
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

    const thatInOffice = new RegExp(`\\bthat\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\s+in\\s+(?:the\\s+)?[A-Za-z' -]{0,40}\\boffice\\b`, 'gi')
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
    const rel = new RegExp(`\\b(?:his|her|their)\\s+(son|daughter|colleague|manager|supervisor|friend)\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\b`, 'gi')
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
    const comm = new RegExp(`\\b(emailed|called|met|contacted|messaged|spoke)\\s+(?:to\\s+)?(${PERSON_CONTEXT_NAME_PATTERN})\\b`, 'g')
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
    const intro = new RegExp(`\\b(my|his|her|their)\\s+name\\s+is\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\b`, 'gi')
    while ((m = intro.exec(text)) !== null) {
      const name = m[2]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.85 })
    }

    // Relationship-owned intro: "wife's name is Julia", "partner's name is Dan".
    const introRelation = new RegExp(`\\b(?:wife|husband|partner|mother|father|brother|sister|friend|colleague|manager)['’]s\\s+name\\s+is\\s+(${PERSON_CONTEXT_NAME_PATTERN})\\b`, 'gi')
    while ((m = introRelation.exec(text)) !== null) {
      const name = m[1]
      const start = m.index + m[0].lastIndexOf(name)
      const end = start + name.length
      if (intersectsLocked(start, end, locked)) continue
      if (!isPersonSpanValid(text, start, end, name)) continue
      out.push({ type: 'PERSON', start, end, score: 0.84 })
    }

    // Subject form at sentence start: "Dan has ...", "Sofia works ...".
    const subjectLead = new RegExp(`(?:^|[.!?]\\s+)(${PERSON_CONTEXT_NAME_PATTERN})\\s+(is|was|has|had|works|worked|lives|lived|moved|joined|arrived|said|wrote)\\b`, 'g')
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
  }

  if (enabled.has('ORG')) {
    const org = /\b[A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,5}\s(?:Ltd\.?|Limited|Inc\.?|LLC|Consulting|Initiative|University|Lab|Labs|Institute|School|Faculty|Foundation|Alliance|Group|Network|Agency|Council|Bank|Office|Department|Systems?)\b/g
    let m
    while ((m = org.exec(text)) !== null) {
      if (m[0].includes(' from ')) continue
      if (isIgnoredEntityPhrase(m[0]) || hasIgnoredEntityContext(text, m.index)) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.75 })
    }

    const orgDepartmental = /\b(?:Department|Institute|School|Faculty|Centre|Center)\s+(?:of|for)\s+[A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,5}\b/g
    while ((m = orgDepartmental.exec(text)) !== null) {
      if (isIgnoredEntityPhrase(m[0])) continue
      if (intersectsLocked(m.index, m.index + m[0].length, locked)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.93 })
    }

    const orgExtended = /\b[A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,5}\s(?:Lab|Labs|Research|Initiative|Alliance|Group|Institute|Network|Foundation)\b/g
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
    const orgContextualSingle = /\b(?:at|in|from|via|with|for|into|joined|joining|works(?:\s+at|\s+in)?|worked(?:\s+at|\s+in)?|working(?:\s+at|\s+in)?|employed(?:\s+at|\s+in)?)\s+([A-Z][A-Za-z0-9&.-]{2,}|[A-Z]{2,})\b/g
    while ((m = orgContextualSingle.exec(text)) !== null) {
      const candidate = m[1]
      const start = m.index + m[0].lastIndexOf(candidate)
      const end = start + candidate.length
      if (hasIgnoredEntityContext(text, start)) continue
      if (intersectsLocked(start, end, locked)) continue
      const lower = candidate.toLowerCase()
      if (FIELD_LABEL_WORDS.has(lower)) continue
      if (PERSON_STOPWORDS.has(lower)) continue
      if (STREET_SUFFIXES.has(lower)) continue
      if (PERSON_REL_WORDS.has(lower)) continue
      if (ORG_CONTEXT_WORDS.has(lower)) continue
      const line = getLineAt(text, start)
      if (isLikelyHeadingLine(line)) continue
      out.push({ type: 'ORG', start, end, score: 0.86 })
    }
  }

  if (enabled.has('ADDRESS')) {
    const address = /\b\d{1,5}[A-Za-z]?\s+(?:[A-Z][A-Za-z' -]*(?:-[A-Z][A-Za-z' -]*)*\s+){0,4}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl|Square|Sq|Plaza|Boulevard|Blvd)\b/g
    let m
    while ((m = address.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.83 })
    }

    const viaStreet = /\bVia\s+[A-Z][A-Za-z' -]*(?:-[A-Z][A-Za-z' -]*)*(?:\s+[A-Z][A-Za-z' -]*(?:-[A-Z][A-Za-z' -]*)*){0,2}\b/g
    while ((m = viaStreet.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.82 })
    }

    // Lightweight location cue: "called Stoke", "in London", "at Manchester City Centre".
    const locationCue = /\b(?:in|at|from|location\s+called)\s+([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b/g
    while ((m = locationCue.exec(text)) !== null) {
      const place = m[1]
      if (isPersonStopword(place)) continue
      if (hasOrgHint(place)) continue
      const idx = m.index + m[0].lastIndexOf(place)
      out.push({ type: 'ADDRESS', start: idx, end: idx + place.length, score: 0.69 })
    }
  }

  return out
}

function detectPersonFromOrganisationPattern(text, enabled, locked = []) {
  const out = []
  const personEnabled = enabled.has('PERSON')
  const orgEnabled = enabled.has('ORG')
  if (!personEnabled && !orgEnabled) return out

  const pattern = /\b([A-Z][a-z]{1,}(?:-[A-Z][a-z]{1,})*)\s+from\s+([A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,6}\s(?:Ltd\.?|Limited|Inc\.?|LLC|Consulting|University|Bank|Council|Office|Agency|Department|School|Faculty|Lab|Labs|Research|Initiative|Alliance|Group|Institute|Network|Foundation|Systems?))\b/g
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

    if (personEnabled && !precededByCapitalizedName && !intersectsLocked(personStart, personEnd, locked) && isPersonCandidateValid(text, personStart, personEnd, person)) {
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
  return `${type}:${value}`
}

function applyReplacements(text, detections, tokenStyle = 'standard', aliasMap = {}) {
  const counters = {}
  const stableMap = {}
  const entities = []
  const out = []
  let i = 0

  for (const d of detections) {
    const original = text.slice(d.start, d.end)
    const normalized = original
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
    const ownCanonical = canonicalEntityKey(d.type, normalized)
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
    .replace(/(\[(?:📍\s*)?Location\s+\d+\])\s*[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/g, '$1')
    .replace(/(\[(?:📍\s*)?Location\s+\d+\])\s*\d\s+[A-Z]{2}\b/g, '$1')
  return { anonymized_text: cleaned, entities, counts: counters }
}

const PRONOUN_REVERSE_MAP = {
  she: 'he',
  her: 'his',
  hers: 'his',
  herself: 'himself',
  he: 'she',
  him: 'her',
  his: 'her',
  himself: 'herself',
}

function applyCaseStyle(source, target) {
  if (!source) return target
  if (source === source.toUpperCase()) return target.toUpperCase()
  if (source === source.toLowerCase()) return target.toLowerCase()
  const isTitleCase = source[0] === source[0].toUpperCase() && source.slice(1) === source.slice(1).toLowerCase()
  if (isTitleCase) return target[0].toUpperCase() + target.slice(1).toLowerCase()
  return target
}

function reverseGenderedPronouns(text) {
  return String(text || '').replace(/\b(she|her|hers|herself|he|him|his|himself)\b/gi, (match) => {
    const replacement = PRONOUN_REVERSE_MAP[match.toLowerCase()]
    if (!replacement) return match
    return applyCaseStyle(match, replacement)
  })
}

function previousWord(text, index) {
  const head = text.slice(0, index)
  const m = head.match(/([A-Za-z]+)\W*$/)
  return m ? m[1].toLowerCase() : ''
}

function nextWord(text, endIndex) {
  const tail = text.slice(endIndex)
  const m = tail.match(/^\W*([A-Za-z]+)/)
  return m ? m[1].toLowerCase() : ''
}

function buildPersonCoreferenceLinks(text, detections) {
  const fullNames = detections
    .filter((d) => d.type === 'PERSON')
    .map((d) => {
      const raw = text.slice(d.start, d.end).trim()
      const cleaned = stripPersonTitle(raw).trim()
      const parts = cleaned.split(/\s+/).filter(Boolean)
      if (parts.length !== 2) return null
      const [first, last] = parts
      if (!NAME_TOKEN_REGEX.test(first) || !NAME_TOKEN_REGEX.test(last)) return null
      const normalized = cleaned.toLowerCase().replace(/\s+/g, ' ')
      return {
        detection: d,
        first: first.toLowerCase(),
        last: last.toLowerCase(),
        canonical: canonicalEntityKey('PERSON', normalized),
      }
    })
    .filter(Boolean)

  if (fullNames.length === 0) {
    return { additions: [], aliasMap: {} }
  }

  const firstNameMap = new Map()
  const lastNameMap = new Map()
  const ambiguousFirst = new Set()
  const ambiguousLast = new Set()

  for (const full of fullNames) {
    const firstExisting = firstNameMap.get(full.first)
    if (!firstExisting) {
      firstNameMap.set(full.first, full.canonical)
    } else if (firstExisting !== full.canonical) {
      ambiguousFirst.add(full.first)
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

  const aliasMap = {}
  for (const [name, canonical] of firstNameMap.entries()) {
    aliasMap[canonicalEntityKey('PERSON', name)] = canonical
  }
  for (const [name, canonical] of lastNameMap.entries()) {
    aliasMap[canonicalEntityKey('PERSON', name)] = canonical
  }

  const additions = []
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

  // Priority order: Email -> URL -> Phone -> Date -> Address -> Organisation -> Person.
  addStage([
    ...structured.filter((d) => d.type === 'EMAIL'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'EMAIL'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'URL'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'URL'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'PHONE'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'PHONE'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'DATE'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'DATE'))),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'ADDRESS'),
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'ADDRESS'))),
    ...detectHeuristics(text, new Set([...enabled].filter((t) => t === 'ADDRESS')), resolved),
  ])
  addStage(detectPersonFromOrganisationPattern(text, enabled, resolved))
  addStage([
    ...structured.filter((d) => d.type === 'ORG'),
    ...detectHeuristics(text, new Set([...enabled].filter((t) => t === 'ORG')), resolved),
  ])
  addStage([
    ...structured.filter((d) => d.type === 'PERSON'),
    ...detectHeuristics(text, new Set([...enabled].filter((t) => t === 'PERSON')), resolved),
  ])

  const coref = enabled.has('PERSON') ? buildPersonCoreferenceLinks(text, resolved) : { additions: [], aliasMap: {} }
  addStage(coref.additions)

  resolved.sort((a, b) => a.start - b.start || a.end - b.end)
  const replaced = applyReplacements(text, resolved, tokenStyle, coref.aliasMap)
  const transformedText = reversePronouns
    ? reverseGenderedPronouns(replaced.anonymized_text)
    : replaced.anonymized_text
  return { ...replaced, anonymized_text: transformedText, cta_visaprep: IMMIGRATION.test(text) }
}
