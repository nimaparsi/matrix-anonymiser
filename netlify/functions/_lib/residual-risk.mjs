const FACTORS = [
  { id: 'rare_role', label: 'rare occupation or unique role wording', weight: 2, pattern: /\b(?:only|sole|principal|staff|distinguished|founding|head of)\b.{0,80}\b(?:engineer|doctor|consultant|analyst|manager|director|officer|lawyer|partner|researcher)\b/i },
  { id: 'precise_location', label: 'precise location', weight: 2, pattern: /\b(?:Stoke-on-Trent|Glasgow|York|Oxford|Manchester|Brighton|Cambridge|London|Leeds|Bristol|Edinburgh|Sheffield)\b|\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/i },
  { id: 'exact_salary', label: 'exact salary or exact monetary value', weight: 2, pattern: /(?:£|\$|€)\s?\d{2,3}(?:,\d{3})+(?:\.\d{2})?\b|\b\d{2,3}(?:,\d{3})+\s?(?:gbp|usd|eur|pounds?|dollars?|euros?)\b/i },
  { id: 'age', label: 'age', weight: 1, pattern: /\b(?:\d{2})\s?(?:years old|year-old)\b|\bage\s*:?\s*\d{2}\b/i },
  { id: 'nationality', label: 'nationality or birthplace', weight: 2, pattern: /\b(?:Iranian|British|American|French|German|Indian|Pakistani|Nigerian|Polish|Romanian|Spanish|Italian|Chinese|born in|born)\b/i },
  { id: 'employer', label: 'employer or organisation context', weight: 1, pattern: /\b(?:at|for|with)\s+[A-Z][A-Za-z&'-]+(?:\s+[A-Z][A-Za-z&'-]+){1,4}\b/i },
  { id: 'specific_date', label: 'specific date', weight: 1, pattern: /\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b/i },
  { id: 'project_name', label: 'project or codename', weight: 1, pattern: /\b(?:project|codename|programme|program)\s+[A-Z][A-Za-z0-9-]+\b/i },
  { id: 'alias_linkage', label: 'alias or account linkage', weight: 2, pattern: /\b(?:username|user|handle|github|slack)\s*[:=]?\s*[a-z][a-z0-9_.-]{3,}\b/i },
]

function classify(score) {
  if (score >= 6) return 'high'
  if (score >= 3) return 'medium'
  if (score > 0) return 'low'
  return 'minimal'
}

export function assessResidualContextRisk(text) {
  const value = String(text || '')
  const factors = FACTORS.filter((factor) => factor.pattern.test(value)).map((factor) => ({ id: factor.id, label: factor.label, weight: factor.weight }))
  const score = factors.reduce((sum, factor) => sum + factor.weight, 0)
  return { risk: classify(score), score, factors }
}
