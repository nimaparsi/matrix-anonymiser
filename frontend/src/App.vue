<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const MAX_CHARS = 50000
const MAX_UPLOAD_BYTES = 8 * 1024 * 1024
const TEXT_EXTENSIONS = new Set(['txt', 'md', 'csv', 'json', 'log'])
const ENGLISH_HINT_WORDS = new Set([
  'the', 'and', 'with', 'for', 'from', 'that', 'this', 'is', 'are', 'was', 'were',
  'have', 'has', 'will', 'would', 'you', 'your', 'their', 'there', 'about', 'before',
  'after', 'meeting', 'email', 'phone', 'address', 'document', 'project', 'report',
])
const PREVIEW_TYPE_ORDER = ['PERSON', 'ORG', 'EMAIL', 'PHONE', 'IP_ADDRESS', 'ADDRESS', 'DATE', 'URL', 'USERNAME', 'COORDINATE', 'FILE_PATH']
let pdfRuntimePromise = null

function apiUrl(path) {
  const base = API_BASE.replace(/\/$/, '')
  return base ? `${base}/api/${path}` : `/api/${path}`
}

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const limitState = ref(null)
const emojiTags = ref(false)
const highlightCensored = ref(true)
const reversePronouns = ref(false)
const redactionMode = ref(false)
const resultSection = ref(null)
const inputArea = ref(null)
const inputHighlighted = ref(false)
const fileBusy = ref(false)
const uploadStatus = ref('')
const dropActive = ref(false)
const copyFeedback = ref('Copy result')

const entityOptions = [
  { key: 'PERSON', label: 'People' },
  { key: 'EMAIL', label: 'Email' },
  { key: 'PHONE', label: 'Phone' },
  { key: 'IP_ADDRESS', label: 'IP address' },
  { key: 'URL', label: 'URL' },
  { key: 'ADDRESS', label: 'Address' },
  { key: 'ORG', label: 'Organisation' },
  { key: 'DATE', label: 'Date' },
  { key: 'USERNAME', label: 'Username' },
  { key: 'COORDINATE', label: 'Coordinate' },
  { key: 'FILE_PATH', label: 'File path' },
]
const allEntityKeys = entityOptions.map((item) => item.key)
const enabled = ref(new Set(allEntityKeys))

const selectedTypes = computed(() => Array.from(enabled.value))
const charsLeft = computed(() => MAX_CHARS - text.value.length)
const canSubmit = computed(() => text.value.trim().length > 0 && !loading.value && selectedTypes.value.length > 0)
const allEnabled = computed(() => allEntityKeys.every((key) => enabled.value.has(key)))
const resultWarning = computed(() => result.value?.warning || '')

const previewCounts = computed(() => lightweightPreviewCounts(text.value))
const previewRows = computed(() => PREVIEW_TYPE_ORDER.map((type) => ({
  type,
  label: previewLabel(type),
  count: previewCounts.value[type] || 0,
})))

const previewLanguageLabel = computed(() => detectLanguageLabel(text.value))
const resultLanguageLabel = computed(() => {
  const raw = String(result.value?.meta?.language || result.value?.meta?.detected_language || '').trim()
  if (!raw || raw.toLowerCase() === 'unknown') {
    return 'Unknown (English recommended)'
  }
  return raw
})

const resultTotalEntities = computed(() => {
  const counts = result.value?.counts || {}
  return Object.values(counts).reduce((sum, item) => sum + Number(item || 0), 0)
})

const summaryLine = computed(() => {
  if (!result.value) return ''
  const total = resultTotalEntities.value
  const processing = Number(result.value?.meta?.processing_ms || 0)
  const timeText = Number.isFinite(processing) && processing > 0 ? `${processing}ms` : 'n/a'
  return `${total} ${total === 1 ? 'entity' : 'entities'} detected · Processing time: ${timeText} · Language: ${resultLanguageLabel.value}`
})
const displayAnonymizedText = computed(() => {
  const raw = result.value?.anonymized_text || ''
  if (emojiTags.value) {
    return raw
      .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, '👤 Person $1')
      .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, '📧 Email $1')
      .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, '📞 Phone $1')
      .replace(/\[(?:🌐\s*)?IP Address\s+(\d+)\]/g, '🌐 IP Address $1')
      .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, '🔗 Web Address $1')
      .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, '📍 Location $1')
      .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, '🏢 Organisation $1')
      .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, '📅 Date $1')
      .replace(/\[(?:🏷\s*)?Username\s+(\d+)\]/g, '🏷 Username $1')
      .replace(/\[(?:🧭\s*)?Coordinate\s+(\d+)\]/g, '🧭 Coordinate $1')
      .replace(/\[(?:🗂\s*)?File Path\s+(\d+)\]/g, '🗂 File Path $1')
      .replace(/\b(👤|📧|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\2\s+(\d+)\b/g, '$1 $2 $3')
  }
  return raw
    .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, 'Person $1')
    .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, 'Email $1')
    .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, 'Phone $1')
    .replace(/\[(?:🌐\s*)?IP Address\s+(\d+)\]/g, 'IP Address $1')
    .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, 'Web Address $1')
    .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, 'Location $1')
    .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, 'Organisation $1')
    .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, 'Date $1')
    .replace(/\[(?:🏷\s*)?Username\s+(\d+)\]/g, 'Username $1')
    .replace(/\[(?:🧭\s*)?Coordinate\s+(\d+)\]/g, 'Coordinate $1')
    .replace(/\[(?:🗂\s*)?File Path\s+(\d+)\]/g, 'File Path $1')
    .replace(/\b(Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\1\s+(\d+)\b/g, '$1 $2')
})

const outputForDisplay = computed(() => {
  const base = displayAnonymizedText.value
  if (!redactionMode.value) return base
  return applyRedactionMode(base)
})

const tokenTooltipMap = computed(() => {
  const map = new Map()
  const entities = Array.isArray(result.value?.entities) ? result.value.entities : []
  const source = text.value

  for (const entity of entities) {
    const original = source.slice(Number(entity.start || 0), Number(entity.end || 0)).trim()
    const replacement = String(entity.replacement || '').trim()
    if (!original || !replacement) continue

    const tooltip = map.get('__raw__') || new Map()
    for (const key of tokenKeysFromReplacement(replacement)) {
      const values = tooltip.get(key) || new Set()
      values.add(original)
      tooltip.set(key, values)
    }
    map.set('__raw__', tooltip)
  }

  const raw = map.get('__raw__')
  if (!raw) return new Map()

  const flattened = new Map()
  for (const [key, values] of raw.entries()) {
    flattened.set(key, Array.from(values).slice(0, 3).join(' / '))
  }
  return flattened
})

const anonymizedRenderHtml = computed(() => {
  const escaped = escapeHtml(outputForDisplay.value)
  const tokenPattern = /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|\[REDACTED\])/g

  if (!highlightCensored.value) {
    return escaped
  }

  return escaped.replace(tokenPattern, (token) => {
    const key = normalizeTokenKey(token)
    const tooltip = redactionMode.value ? '' : tokenTooltipMap.value.get(key) || ''
    const tooltipAttr = tooltip ? ` title="${escapeHtml(`Original: ${tooltip}`)}"` : ''
    return `<mark class="token-highlight"${tooltipAttr}>${token}</mark>`
  })
})

function previewLabel(type) {
  switch (type) {
    case 'PERSON': return 'Person'
    case 'ORG': return 'Organisation'
    case 'EMAIL': return 'Email'
    case 'PHONE': return 'Phone'
    case 'IP_ADDRESS': return 'IP address'
    case 'ADDRESS': return 'Address'
    case 'DATE': return 'Date'
    case 'URL': return 'URL'
    case 'USERNAME': return 'Username'
    case 'COORDINATE': return 'Coordinate'
    case 'FILE_PATH': return 'File path'
    default: return type
  }
}

function detectLanguageLabel(input) {
  const words = String(input || '')
    .toLowerCase()
    .match(/[a-z]{2,}/g) || []
  if (words.length < 5) return 'Unknown (English recommended)'
  let hits = 0
  for (const word of words) {
    if (ENGLISH_HINT_WORDS.has(word)) hits += 1
  }
  const ratio = hits / words.length
  return ratio >= 0.08 ? 'English' : 'Unknown (English recommended)'
}

function lightweightPreviewCounts(input) {
  const value = String(input || '')
  const counts = {
    PERSON: 0,
    ORG: 0,
    EMAIL: 0,
    PHONE: 0,
    IP_ADDRESS: 0,
    ADDRESS: 0,
    DATE: 0,
    URL: 0,
    USERNAME: 0,
    COORDINATE: 0,
    FILE_PATH: 0,
  }

  if (!value.trim()) return counts

  const patterns = {
    EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
    URL: /https?:\/\/[^\s]+/gi,
    PHONE: /\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b/g,
    IP_ADDRESS: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
    DATE: /\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:,?\s+\d{2,4})?)\b/gi,
    ADDRESS: /\b\d{1,5}\s+[A-Z][A-Za-z' -]{1,40}\s(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Way|Terrace|Terr|Court|Ct|Place|Pl)\b(?:,\s*[A-Z][A-Za-z' -]{1,40}\s+[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b|,\s*[A-Z][A-Za-z' -]{1,40}\b)?/g,
    ORG: /\b[A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,4}\s(?:Ltd|Limited|Inc|LLC|Lab|Labs|Research|Initiative|Alliance|Group|Institute|Network|Foundation|University|Bank|Council|Agency|Department)\b/g,
    PERSON: /\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b/g,
    USERNAME: /@?[A-Za-z][A-Za-z0-9._-]{2,}/g,
    COORDINATE: /\b-?\d{1,2}\.\d{3,}\s*,\s*-?\d{1,3}\.\d{3,}\b/g,
    FILE_PATH: /\b(?:[A-Za-z]:\\|\/)?(?:[\w.-]+[\/\\])+[\w.-]+\b/g,
  }

  for (const type of Object.keys(patterns)) {
    const regex = patterns[type]
    regex.lastIndex = 0
    const seen = new Set()
    let m
    while ((m = regex.exec(value)) !== null) {
      const key = `${m.index}:${m[0].toLowerCase()}`
      if (!seen.has(key)) {
        seen.add(key)
        counts[type] += 1
      }
    }
  }

  return counts
}

function normalizeTokenKey(token) {
  const cleaned = String(token || '')
    .replace(/\[|\]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^(👤|📧|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s*/, '')
  return cleaned.toLowerCase()
}

function tokenKeysFromReplacement(replacement) {
  const forms = new Set()
  const raw = String(replacement || '').trim()
  const clean = raw.replace(/^\[|\]$/g, '').trim()
  const plain = clean.replace(/^(👤|📧|📞|🔗|📍|🏢|📅)\s*/, '')

  const addForm = (value) => {
    const key = normalizeTokenKey(value)
    if (key) forms.add(key)
  }

  addForm(raw)
  addForm(clean)
  addForm(plain)
  addForm(`[${plain}]`)

  const parsed = plain.match(/^(Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+(\d+)$/i)
  if (parsed) {
    const label = parsed[1]
    const number = parsed[2]
    const emojiByLabel = {
      person: '👤',
      email: '📧',
      phone: '📞',
      'ip address': '🌐',
      'web address': '🔗',
      location: '📍',
      organisation: '🏢',
      date: '📅',
      username: '🏷',
      coordinate: '🧭',
      'file path': '🗂',
    }
    const emoji = emojiByLabel[label.toLowerCase()]
    if (emoji) {
      addForm(`${emoji} ${label} ${number}`)
      addForm(`[${emoji} ${label} ${number}]`)
    }
  }

  return Array.from(forms)
}

function applyRedactionMode(value) {
  return String(value || '').replace(
    /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b)/g,
    '[REDACTED]',
  )
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
function toggleType(key) {
  const current = new Set(enabled.value)
  if (current.has(key)) {
    current.delete(key)
  } else {
    current.add(key)
  }
  enabled.value = current
}

function toggleAllTypes() {
  if (allEnabled.value) {
    enabled.value = new Set()
    return
  }
  enabled.value = new Set(allEntityKeys)
}

function handleInputKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    anonymize()
  }
}

async function anonymize() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''
  limitState.value = null
  result.value = null

  try {
    const res = await fetch(apiUrl('anonymize'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        text: text.value,
        entity_types: selectedTypes.value,
        tag_style: emojiTags.value ? 'emoji' : 'standard',
        reverse_pronouns: reversePronouns.value,
      })
    })

    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const detailObject = typeof data?.detail === 'object' && data.detail ? data.detail : null
      if (res.status === 429 && detailObject?.code === 'USAGE_LIMIT_EXCEEDED') {
        limitState.value = {
          message: detailObject.message || 'Daily limit reached',
          used: Number(detailObject.used || 0),
          limit: Number(detailObject.limit || 0)
        }
        result.value = null
        return
      }

      const detail = typeof data?.detail === 'string' ? data.detail : detailObject?.message || 'Anonymisation failed'
      throw new Error(detail)
    }

    result.value = data
    copyFeedback.value = 'Copy result'
    await nextTick()
    resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    error.value = e.message || 'Unexpected error'
  } finally {
    loading.value = false
  }
}

function getFileExtension(name) {
  const value = String(name || '')
  const dot = value.lastIndexOf('.')
  if (dot < 0) return ''
  return value.slice(dot + 1).toLowerCase()
}

function isTextLikeFile(file) {
  const ext = getFileExtension(file?.name)
  if (TEXT_EXTENSIONS.has(ext)) return true
  const type = String(file?.type || '').toLowerCase()
  return type.startsWith('text/') || type === 'application/json'
}

function rebuildPdfPageText(content) {
  const items = content.items
    .filter((item) => 'str' in item && item.str)
    .map((item) => ({
      str: String(item.str || ''),
      x: Array.isArray(item.transform) ? Number(item.transform[4] || 0) : 0,
      y: Array.isArray(item.transform) ? Number(item.transform[5] || 0) : 0,
      width: Number(item.width || 0),
      hasEOL: Boolean(item.hasEOL),
    }))

  if (items.length === 0) return ''

  const lines = []
  let currentLine = ''
  let prev = null

  const pushLine = () => {
    const clean = currentLine.replace(/[ \t]+/g, ' ').trim()
    if (clean) lines.push(clean)
    currentLine = ''
  }

  for (const token of items) {
    const tokenText = token.str.replace(/\s+/g, ' ')
    if (!tokenText.trim()) continue

    if (prev) {
      const yDelta = Math.abs(token.y - prev.y)
      const movedBack = token.x + 1 < prev.x
      if (prev.hasEOL || (yDelta > 2 && movedBack)) {
        pushLine()
      } else if (currentLine) {
        const prevRight = prev.x + Math.max(prev.width, 0)
        const gap = token.x - prevRight
        const prevAvgChar = prev.str.length > 0 ? prev.width / prev.str.length : 0
        const gapThreshold = Math.max(1.5, prevAvgChar * 0.45)
        const needsSpace = gap > gapThreshold && !currentLine.endsWith(' ') && !tokenText.startsWith(' ')
        if (needsSpace) currentLine += ' '
      }
    }

    currentLine += tokenText
    prev = token

    if (token.hasEOL) {
      pushLine()
      prev = null
    }
  }

  pushLine()
  return lines.join('\n')
}

async function extractPdfText(file) {
  if (!pdfRuntimePromise) {
    pdfRuntimePromise = Promise.all([
      import('pdfjs-dist/legacy/build/pdf.mjs'),
      import('pdfjs-dist/legacy/build/pdf.worker.mjs?url'),
    ]).then(([pdfjs, worker]) => {
      pdfjs.GlobalWorkerOptions.workerSrc = worker.default
      return pdfjs
    })
  }
  const { getDocument } = await pdfRuntimePromise

  const bytes = new Uint8Array(await file.arrayBuffer())
  const pdf = await getDocument({ data: bytes }).promise
  const pages = []
  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum += 1) {
    const page = await pdf.getPage(pageNum)
    const content = await page.getTextContent({
      normalizeWhitespace: true,
      disableCombineTextItems: false,
    })
    const pageText = rebuildPdfPageText(content)
    pages.push(pageText)
  }
  return pages.join('\n\n')
}

function normalizeLoadedText(raw) {
  return String(raw || '').replace(/\u0000/g, '').trim()
}

async function loadFile(file) {
  if (!file) return

  fileBusy.value = true
  uploadStatus.value = ''
  error.value = ''
  result.value = null

  try {
    if (file.size > MAX_UPLOAD_BYTES) {
      throw new Error('File too large. Max 8MB for upload in this version.')
    }

    let loaded = ''
    const ext = getFileExtension(file.name)
    if (ext === 'pdf' || file.type === 'application/pdf') {
      uploadStatus.value = 'Reading PDF locally...'
      loaded = await extractPdfText(file)
    } else if (isTextLikeFile(file)) {
      uploadStatus.value = 'Reading text file locally...'
      loaded = await file.text()
    } else {
      throw new Error('Unsupported file type. Use PDF or text files (.txt, .md, .csv, .json, .log).')
    }

    const normalized = normalizeLoadedText(loaded)
    if (!normalized) {
      throw new Error('No readable text found in this file.')
    }

    if (normalized.length > MAX_CHARS) {
      text.value = normalized.slice(0, MAX_CHARS)
      uploadStatus.value = `Loaded ${file.name} (truncated to ${MAX_CHARS.toLocaleString()} characters).`
    } else {
      text.value = normalized
      uploadStatus.value = `Loaded ${file.name}.`
    }

    await nextTick()
    inputArea.value?.focus({ preventScroll: true })
    inputArea.value?.select()
  } catch (e) {
    error.value = e.message || 'Failed to read file'
    uploadStatus.value = ''
  } finally {
    fileBusy.value = false
  }
}

async function handleFileSelect(event) {
  const input = event.target
  const file = input.files?.[0]
  if (!file) return
  await loadFile(file)
  input.value = ''
}

function handleDragOver(event) {
  event.preventDefault()
  dropActive.value = true
}

function handleDragLeave() {
  dropActive.value = false
}

async function handleDrop(event) {
  event.preventDefault()
  dropActive.value = false

  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    await loadFile(files[0])
    return
  }

  const droppedText = String(event.dataTransfer?.getData('text/plain') || '').trim()
  if (!droppedText) return

  text.value = droppedText.length > MAX_CHARS ? droppedText.slice(0, MAX_CHARS) : droppedText
  uploadStatus.value = droppedText.length > MAX_CHARS
    ? `Dropped text was truncated to ${MAX_CHARS.toLocaleString()} characters.`
    : 'Dropped text loaded.'
}

async function copyOutput() {
  const output = outputForDisplay.value
  if (!output) return
  await navigator.clipboard.writeText(output)
  copyFeedback.value = 'Copied ✓'
  window.setTimeout(() => {
    copyFeedback.value = 'Copy result'
  }, 1300)
}

function downloadOutput() {
  const output = outputForDisplay.value
  if (!output) return
  const blob = new Blob([output], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'anonymized.txt'
  a.click()
  URL.revokeObjectURL(url)
}

async function upgrade() {
  error.value = ''
  try {
    const successUrl = `${window.location.origin}/`
    const cancelUrl = `${window.location.origin}/`
    const res = await fetch(apiUrl('billing/create-checkout'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ success_url: successUrl, cancel_url: cancelUrl })
    })

    if (res.ok) {
      const data = await res.json()
      window.location.href = data.url
      return
    }

    const devRes = await fetch(apiUrl('billing/dev-upgrade'), {
      method: 'POST',
      credentials: 'include'
    })
    if (!devRes.ok) {
      throw new Error('Upgrade unavailable right now')
    }
  } catch (e) {
    error.value = e.message || 'Upgrade failed'
  }
}

onMounted(async () => {
  await nextTick()
  inputHighlighted.value = true
  const desktopPointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches
  if (desktopPointer) {
    inputArea.value?.focus({ preventScroll: true })
  }
  window.setTimeout(() => {
    inputHighlighted.value = false
  }, 1800)

  const sessionId = new URLSearchParams(window.location.search).get('session_id')
  if (sessionId) {
    try {
      await fetch(`${apiUrl('billing/activate')}?session_id=${encodeURIComponent(sessionId)}`, {
        credentials: 'include'
      })
    } catch (_) {
      // Do not block normal app usage if billing activation fails.
    }
  }
})
</script>

<template>
  <div class="matrix-bg" aria-hidden="true"></div>
  <main class="container">
    <header class="hero">
      <p class="eyebrow">Matrix Privacy Engine</p>
      <div class="hero-title-row">
        <svg :class="['brand-icon', { 'is-processing': loading }]" viewBox="0 0 64 64" role="img" aria-label="Matrix Anonymiser icon">
          <defs>
            <linearGradient id="heroRadarGlow" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#7cffbc" />
              <stop offset="100%" stop-color="#13db7b" />
            </linearGradient>
          </defs>
          <rect class="detector-frame" x="2" y="2" width="60" height="60" rx="12" fill="#07110f" stroke="#2f5e4b" />
          <g class="detector-rings">
            <circle cx="32" cy="32" r="20" fill="none" stroke="#1f4a3a" stroke-width="1.6" />
            <circle cx="32" cy="32" r="13" fill="none" stroke="#1c4033" stroke-width="1.4" />
            <circle cx="32" cy="32" r="6" fill="none" stroke="#1a392d" stroke-width="1.2" />
          </g>
          <g class="detector-sweep">
            <path d="M32 32 L48 22" stroke="url(#heroRadarGlow)" stroke-width="2.6" stroke-linecap="round" />
            <circle cx="48" cy="22" r="2.8" fill="url(#heroRadarGlow)" />
          </g>
          <circle cx="32" cy="32" r="2.4" fill="#9dffd0" />
        </svg>
        <h1 class="headline-gradient">Sanitise sensitive text before AI sees it.</h1>
      </div>
      <p class="subtitle">Turn sensitive text into safe-to-share content in seconds.</p>
      <p class="trust-line">Your text is processed in memory and never stored.</p>
      <div class="trust-row">
        <span>No text storage</span>
        <span>Fast one-click anonymisation</span>
        <span>Redacted telemetry only</span>
      </div>
    </header>

    <section class="panel">
      <label for="input" class="label">Paste text</label>
      <div class="upload-row">
        <label for="file-upload" class="btn upload-btn">
          {{ fileBusy ? 'Reading file...' : 'Upload PDF or text' }}
        </label>
        <input
          id="file-upload"
          class="file-input"
          type="file"
          accept=".pdf,.txt,.md,.csv,.json,.log,text/plain,application/pdf,application/json"
          :disabled="fileBusy || loading"
          @change="handleFileSelect"
        />
      </div>
      <p v-if="uploadStatus" class="charline">{{ uploadStatus }}</p>
      <div
        :class="['drop-zone', { active: dropActive }]"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <textarea
          id="input"
          ref="inputArea"
          :class="{ 'load-highlight': inputHighlighted }"
          v-model="text"
          rows="10"
          maxlength="50000"
          placeholder="Paste or drop text / documents here"
          @keydown="handleInputKeydown"
        ></textarea>
      </div>
      <div class="charline">{{ charsLeft }} characters remaining</div>

      <div class="preview-panel" v-if="text.trim().length">
        <p class="preview-title">Detected entities</p>
        <div class="preview-grid">
          <span v-for="row in previewRows" :key="row.type" class="preview-item">
            {{ row.label }} ({{ row.count }})
          </span>
        </div>
        <p class="preview-language">Language: {{ previewLanguageLabel }}</p>
      </div>

      <div class="entity-filter">
        <p class="entity-filter-title">Entities to anonymise</p>
        <div class="entity-all-row">
          <button
            type="button"
            :class="['chip', { active: allEnabled }]"
            @click="toggleAllTypes"
          >
            All
          </button>
        </div>
        <div class="toggles grouped">
          <button
            v-for="item in entityOptions"
            :key="item.key"
            type="button"
            :class="['chip', { active: enabled.has(item.key) }]"
            @click="toggleType(item.key)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>

      <div class="option-row">
        <label class="friendly-option">
          <input v-model="emojiTags" type="checkbox" />
          Emoji tags
        </label>
        <label class="friendly-option">
          <input v-model="reversePronouns" type="checkbox" />
          Reverse pronouns
        </label>
        <label class="friendly-option">
          <input v-model="redactionMode" type="checkbox" />
          Replace entities with [REDACTED]
        </label>
      </div>
      <div class="charline">These options apply on the next anonymise run.</div>

      <div class="actions">
        <button type="button" class="btn primary" :disabled="!canSubmit" @click="anonymize">
          {{ loading ? 'Processing...' : 'Anonymise' }}
        </button>
      </div>
      <div v-if="limitState" class="limit-card" role="status" aria-live="polite">
        <p class="limit-title">{{ limitState.message }}</p>
        <p class="limit-copy">{{ limitState.used }}/{{ limitState.limit }} free anonymisations used today.</p>
        <div class="actions limit-actions">
          <button type="button" class="btn primary" @click="upgrade">Go Pro</button>
          <button type="button" class="btn" @click="limitState = null">Dismiss</button>
        </div>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section v-if="result" ref="resultSection" class="grid">
      <div v-if="resultWarning" class="warning-banner" role="status" aria-live="polite">
        ⚠ {{ resultWarning }}
      </div>
      <article class="panel">
        <h2>Original</h2>
        <pre class="text-block">{{ text }}</pre>
      </article>
      <article class="panel anonymized-panel">
        <div class="panel-title-row">
          <h2>Anonymised</h2>
          <button type="button" class="btn compact" @click="copyOutput">{{ copyFeedback }}</button>
        </div>
        <p class="success-indicator">✓ {{ resultTotalEntities }} {{ resultTotalEntities === 1 ? 'entity' : 'entities' }} anonymised</p>
        <div class="option-row">
          <label class="friendly-option">
            <input v-model="highlightCensored" type="checkbox" />
            Highlight censored words
          </label>
        </div>
        <pre class="text-block" v-html="anonymizedRenderHtml"></pre>
        <div class="actions">
          <button type="button" class="btn" @click="downloadOutput">Download .txt</button>
        </div>
      </article>
    </section>

    <section v-if="result" class="panel">
      <h2>Detection Summary</h2>
      <p class="meta">{{ summaryLine }}</p>
      <div class="counts">
        <span v-for="(count, key) in result.counts" :key="key" class="count-item">{{ key }}: {{ count }}</span>
      </div>
      <div class="actions">
        <button type="button" class="btn" @click="upgrade">Advanced export features</button>
      </div>
    </section>

    <section v-if="result?.cta_visaprep" class="panel cta">
      <h2>Need immigration-specific help next?</h2>
      <p>Your text looks immigration-related. You can continue safely with redacted content on Visaprep.</p>
      <a href="https://visaprep.uk" target="_blank" rel="noreferrer" class="btn primary">Open Visaprep</a>
    </section>

    <footer class="site-footer">
      Built by Nima Parsi ·
      <a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">
        Open source on GitHub
      </a> ·
      <a href="/privacy.html">Privacy</a>
    </footer>
  </main>
</template>
