const SUPPORTED = new Set(['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE'])
const PERSON_STOPWORDS = new Set([
  'The', 'A', 'An', 'And', 'But', 'Or', 'If', 'For', 'In', 'On', 'At', 'By', 'From', 'To', 'Of', 'With',
  'No', 'Yes', 'Every', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
  'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
  'Mr', 'Mrs', 'Ms', 'Dr', 'UK', 'UKVI', 'Home', 'Office', 'Visa', 'City', 'Street', 'Road',
  'He', 'She', 'They', 'Them', 'His', 'Her', 'Hers', 'Their', 'Theirs', 'We', 'I', 'You', 'It', 'Its', 'Our', 'Ours',
  'Time', 'Person', 'Email', 'Phone', 'Address', 'Organisation', 'Organization', 'Date'
].map((x) => x.toLowerCase()))
const PERSON_CONTEXT_VERBS = new Set([
  'is', 'was', 'were', 'has', 'had', 'have', 'said', 'told', 'asked', 'wrote', 'sent', 'moved',
  'worked', 'arrived', 'sat', 'lived', 'called', 'emailed', 'met', 'joined', 'left', 'went', 'came',
  'applied', 'rented', 'realized', 'realised',
])
const ORG_HINT_WORDS = new Set([
  'lab', 'labs', 'research', 'initiative', 'alliance', 'group', 'institute', 'network',
  'foundation', 'university', 'bank', 'council', 'office', 'agency', 'department',
  'energy', 'urban', 'coastal', 'ecologic', 'future', 'horizon', 'growth',
])
const FIELD_LABEL_WORDS = new Set(['person', 'email', 'phone', 'address', 'organisation', 'organization', 'date'])

function isPersonStopword(token) {
  return PERSON_STOPWORDS.has(String(token || '').toLowerCase())
}

function hasOrgHint(text) {
  const words = String(text || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]+/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
  return words.some((w) => ORG_HINT_WORDS.has(w))
}

const REGEX = {
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  PHONE: /\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b/g,
  URL: /\bhttps?:\/\/[^\s]+\b/gi,
  UK_REF: /\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b/gi,
  PASSPORT: /\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b/g,
  DATE: /\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}\s?(?:am|pm)?|\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})\b/gi,
  UK_POSTCODE: /\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/gi,
  ADDRESS_UK_FULL: /\b\d{1,5}\s+[A-Z][A-Za-z' -]{1,40}\s(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl)\b(?:,\s*[A-Z][A-Za-z' -]{1,40})?(?:\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2})?/g,
}

const IMMIGRATION = /\b(visa|ukvi|uan|gwf|cas|cos|sponsor|brp|ilr|immigration|home office)\b/i
const TOKEN_META = {
  PERSON: { label: 'Person', emoji: '👤' },
  EMAIL: { label: 'Email', emoji: '📧' },
  PHONE: { label: 'Phone', emoji: '📞' },
  ADDRESS: { label: 'Location', emoji: '📍' },
  ORG: { label: 'Organisation', emoji: '🏢' },
  DATE: { label: 'Date', emoji: '📅' },
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
      out.push({ type, start, end, score })
    }
  }

  add('EMAIL', REGEX.EMAIL)
  add('PHONE', REGEX.PHONE)
  add('DATE', REGEX.DATE)

  if (enabled.has('ADDRESS')) {
    // Prefer full address spans first to avoid partial leaks.
    REGEX.ADDRESS_UK_FULL.lastIndex = 0
    let m
    while ((m = REGEX.ADDRESS_UK_FULL.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.995 })
    }

    // Capture city + postcode chunks even when street portion is missing/ambiguous.
    const cityPostcode = /\b[A-Z][A-Za-z' -]{1,40}\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/g
    while ((m = cityPostcode.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.96 })
    }

    for (const key of ['URL', 'UK_REF', 'PASSPORT']) {
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
  }

  for (const line of lines) {
    const m = line.match(/^\s*([A-Za-z]+)\s*:\s*(.+?)\s*$/)
    if (m) {
      const label = m[1].toLowerCase()
      const mapped = labelMap[label]
      if (mapped && enabled.has(mapped)) {
        const value = m[2]
        const valueStartInLine = line.indexOf(value)
        if (valueStartInLine >= 0) {
          out.push({
            type: mapped,
            start: offset + valueStartInLine,
            end: offset + valueStartInLine + value.length,
            score: 0.995,
          })
        }
      }
    }
    offset += line.length + 1
  }
  return out
}

function detectInlineLabeledFields(text, enabled) {
  const out = []
  const labelMap = {
    person: 'PERSON',
    email: 'EMAIL',
    phone: 'PHONE',
    address: 'ADDRESS',
    organisation: 'ORG',
    organization: 'ORG',
    date: 'DATE',
  }
  const labelRegex = /\b(Person|Email|Phone|Address|Organisation|Organization|Date)\b\s*:?\s*/gi
  const matches = Array.from(text.matchAll(labelRegex))
  if (matches.length === 0) return out

  for (let i = 0; i < matches.length; i++) {
    const m = matches[i]
    const label = m[1].toLowerCase()
    const mapped = labelMap[label]
    if (!mapped || !enabled.has(mapped)) continue

    const valueStart = (m.index ?? 0) + m[0].length
    let valueEnd = text.length
    if (i + 1 < matches.length) valueEnd = matches[i + 1].index ?? text.length

    const raw = text.slice(valueStart, valueEnd)
    let segment = raw.replace(/^[\s,:-]+/, '').replace(/[\s,;:.]+$/, '')
    segment = extractLabeledValue(segment, mapped)
    if (!segment) continue

    const relative = raw.indexOf(segment)
    if (relative < 0) continue

    out.push({
      type: mapped,
      start: valueStart + relative,
      end: valueStart + relative + segment.length,
      score: 0.997,
    })
  }

  return out
}

function extractLabeledValue(segment, type) {
  if (!segment) return ''
  if (type === 'EMAIL') {
    const m = segment.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/)
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
    const m = segment.match(/[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2}/)
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

function detectHeuristics(text, enabled) {
  const out = []
  if (enabled.has('PERSON')) {
    const person = /\b(?:Mr|Mrs|Ms|Dr)\.?\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?\b|\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b/g
    let m
    while ((m = person.exec(text)) !== null) {
      const parts = m[0].replace(/\./g, '').split(/\s+/).filter(Boolean)
      const hasBadPart = parts.some((p) => isPersonStopword(p))
      const orgish = hasOrgHint(m[0])
      if (hasBadPart || orgish) continue
      out.push({ type: 'PERSON', start: m.index, end: m.index + m[0].length, score: 0.8 })
    }

    // Single-name detection for repeated capitalized names (e.g. "Anna" used multiple times).
    const single = /\b[A-Z][a-z]{2,}\b/g
    const counts = new Map()
    const matches = []
    while ((m = single.exec(text)) !== null) {
      const token = m[0]
      if (isPersonStopword(token)) continue
      counts.set(token, (counts.get(token) || 0) + 1)
      matches.push({ token, start: m.index, end: m.index + token.length })
    }
    for (const hit of matches) {
      if ((counts.get(hit.token) || 0) < 2) continue
      out.push({ type: 'PERSON', start: hit.start, end: hit.end, score: 0.7 })
    }

    // Sentence-start single-name detection with verb context (e.g. "Kamran has arrived...").
    const sentenceLead = /(?:^|[.!?\n]\s+)([A-Z][a-z]{2,})\s+([a-z][a-z'-]{1,24})/g
    while ((m = sentenceLead.exec(text)) !== null) {
      const name = m[1]
      const verb = m[2].toLowerCase()
      if (isPersonStopword(name)) continue
      if (!PERSON_CONTEXT_VERBS.has(verb)) continue
      const idx = m.index + m[0].indexOf(name)
      out.push({ type: 'PERSON', start: idx, end: idx + name.length, score: 0.78 })
    }

    // Kinship/relationship context (e.g. "his son Brian", "my friend Kamran").
    const kinship = /\b(?:son|daughter|father|mother|brother|sister|husband|wife|friend|colleague|partner)\s+([A-Z][a-z]{2,})\b/g
    while ((m = kinship.exec(text)) !== null) {
      const name = m[1]
      if (isPersonStopword(name)) continue
      const idx = m.index + m[0].lastIndexOf(name)
      out.push({ type: 'PERSON', start: idx, end: idx + name.length, score: 0.82 })
    }
  }

  if (enabled.has('ORG')) {
    const org = /\b[A-Z][\w&' -]{1,40}\s(?:Ltd|Limited|Inc|LLC|University|Bank|Council|Office|Agency|Department)\b/g
    let m
    while ((m = org.exec(text)) !== null) {
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.75 })
    }
    const orgExtended = /\b[A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,5}\s(?:Lab|Labs|Research|Initiative|Alliance|Group|Institute|Network|Foundation)\b/g
    while ((m = orgExtended.exec(text)) !== null) {
      const first = (m[0].split(/\s+/)[0] || '').toLowerCase()
      if (FIELD_LABEL_WORDS.has(first)) continue
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.82 })
    }
  }

  if (enabled.has('ADDRESS')) {
    const address = /\b\d{1,5}\s+[A-Z][\w' -]{2,40}\s(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way)\b/g
    let m
    while ((m = address.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.83 })
    }

    // Lightweight location cue: "called Stoke", "in London", "at Manchester City Centre".
    const locationCue = /\b(?:called|in|at|from)\s+([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b/g
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

function applyReplacements(text, detections, tokenStyle = 'standard') {
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
    const canonical = `${d.type}:${normalized}`
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
  return { anonymized_text: out.join(''), entities, counts: counters }
}

export function anonymizeText(text, entityTypes, options = {}) {
  const tokenStyle = options.tokenStyle === 'emoji' ? 'emoji' : 'standard'
  const enabled = new Set(entityTypes.filter((t) => SUPPORTED.has(t)))
  const resolved = []
  const addStage = (detections) => {
    const stage = resolveOverlaps(detections)
    for (const det of stage) {
      if (!overlapsAny(det, resolved)) resolved.push(det)
    }
  }

  // Priority order: structured fields -> email -> phone -> date -> address -> org -> person.
  addStage([
    ...detectStructuredFields(text, enabled),
    ...detectInlineLabeledFields(text, enabled),
  ])
  addStage(detectRegex(text, new Set([...enabled].filter((t) => t === 'EMAIL'))))
  addStage(detectRegex(text, new Set([...enabled].filter((t) => t === 'PHONE'))))
  addStage(detectRegex(text, new Set([...enabled].filter((t) => t === 'DATE'))))
  addStage([
    ...detectRegex(text, new Set([...enabled].filter((t) => t === 'ADDRESS'))),
    ...detectHeuristics(text, new Set([...enabled].filter((t) => t === 'ADDRESS'))),
  ])
  addStage(detectHeuristics(text, new Set([...enabled].filter((t) => t === 'ORG'))))
  addStage(detectHeuristics(text, new Set([...enabled].filter((t) => t === 'PERSON'))))

  resolved.sort((a, b) => a.start - b.start || a.end - b.end)
  const replaced = applyReplacements(text, resolved, tokenStyle)
  return { ...replaced, cta_visaprep: IMMIGRATION.test(text) }
}
