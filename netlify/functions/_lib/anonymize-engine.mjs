const SUPPORTED = new Set(['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE'])
const PERSON_STOPWORDS = new Set([
  'The', 'A', 'An', 'And', 'But', 'Or', 'If', 'For', 'In', 'On', 'At', 'By', 'From', 'To', 'Of', 'With',
  'No', 'Yes', 'Every', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
  'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
  'Mr', 'Mrs', 'Ms', 'Dr', 'UK', 'UKVI', 'Home', 'Office', 'Visa', 'City', 'Street', 'Road'
])

const REGEX = {
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  PHONE: /\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b/g,
  URL: /\bhttps?:\/\/[^\s]+\b/gi,
  UK_REF: /\b(?:UAN|GWF|CAS|COS|CoS)[-:\s]*[A-Z0-9]{5,16}\b/gi,
  PASSPORT: /\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b\d{9}\b/g,
  DATE: /\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b/gi,
}

const IMMIGRATION = /\b(visa|ukvi|uan|gwf|cas|cos|sponsor|brp|ilr|immigration|home office)\b/i

function detectRegex(text, enabled) {
  const out = []
  const add = (type, regex, score = 0.99) => {
    if (!enabled.has(type)) return
    regex.lastIndex = 0
    let m
    while ((m = regex.exec(text)) !== null) {
      out.push({ type, start: m.index, end: m.index + m[0].length, score })
    }
  }

  add('EMAIL', REGEX.EMAIL)
  add('PHONE', REGEX.PHONE)
  add('DATE', REGEX.DATE)

  for (const key of ['URL', 'UK_REF', 'PASSPORT']) {
    REGEX[key].lastIndex = 0
    let m
    while ((m = REGEX[key].exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.95 })
    }
  }

  return out
}

function detectHeuristics(text, enabled) {
  const out = []
  if (enabled.has('PERSON')) {
    const person = /\b(?:Mr|Mrs|Ms|Dr)\.?\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?\b|\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b/g
    let m
    while ((m = person.exec(text)) !== null) {
      const parts = m[0].replace(/\./g, '').split(/\s+/).filter(Boolean)
      const hasBadPart = parts.some((p) => PERSON_STOPWORDS.has(p))
      if (hasBadPart) continue
      out.push({ type: 'PERSON', start: m.index, end: m.index + m[0].length, score: 0.8 })
    }

    // Single-name detection for repeated capitalized names (e.g. "Anna" used multiple times).
    const single = /\b[A-Z][a-z]{2,}\b/g
    const counts = new Map()
    const matches = []
    while ((m = single.exec(text)) !== null) {
      const token = m[0]
      if (PERSON_STOPWORDS.has(token)) continue
      counts.set(token, (counts.get(token) || 0) + 1)
      matches.push({ token, start: m.index, end: m.index + token.length })
    }
    for (const hit of matches) {
      if ((counts.get(hit.token) || 0) < 2) continue
      out.push({ type: 'PERSON', start: hit.start, end: hit.end, score: 0.7 })
    }
  }

  if (enabled.has('ORG')) {
    const org = /\b[A-Z][\w&' -]{1,40}\s(?:Ltd|Limited|Inc|LLC|University|Bank|Council|Office|Agency|Department)\b/g
    let m
    while ((m = org.exec(text)) !== null) {
      out.push({ type: 'ORG', start: m.index, end: m.index + m[0].length, score: 0.75 })
    }
  }

  if (enabled.has('ADDRESS')) {
    const address = /\b\d{1,5}\s+[A-Z][\w' -]{2,40}\s(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way)\b/g
    let m
    while ((m = address.exec(text)) !== null) {
      out.push({ type: 'ADDRESS', start: m.index, end: m.index + m[0].length, score: 0.83 })
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

function applyReplacements(text, detections) {
  const counters = {}
  const entities = []
  const out = []
  let i = 0

  for (const d of detections) {
    counters[d.type] = (counters[d.type] || 0) + 1
    const replacement = `[${d.type}_${counters[d.type]}]`
    out.push(text.slice(i, d.start))
    out.push(replacement)
    entities.push({ type: d.type, start: d.start, end: d.end, replacement, confidence: Number(d.score.toFixed(3)) })
    i = d.end
  }

  out.push(text.slice(i))
  return { anonymized_text: out.join(''), entities, counts: counters }
}

export function anonymizeText(text, entityTypes) {
  const enabled = new Set(entityTypes.filter((t) => SUPPORTED.has(t)))
  const hits = [...detectRegex(text, enabled), ...detectHeuristics(text, enabled)]
  const resolved = resolveOverlaps(hits)
  const replaced = applyReplacements(text, resolved)
  return { ...replaced, cta_visaprep: IMMIGRATION.test(text) }
}
