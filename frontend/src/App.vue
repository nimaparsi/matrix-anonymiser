<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const MAX_CHARS = 5000
const MAX_UPLOAD_BYTES = 8 * 1024 * 1024
const TEXT_EXTENSIONS = new Set(['txt', 'md', 'csv', 'json', 'log'])
const ENTITY_PREFS_KEY = 'matrix_anonymiser_entity_types_v1'
const DEFAULT_ENTITY_KEYS = ['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL', 'COMPANY_REGISTRATION_NUMBER', 'BOOKING_REFERENCE', 'TICKET_REFERENCE', 'ORDER_ID', 'TRANSACTION_ID']
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
const protectAllSensitive = ref(true)
const submitGlow = ref(false)

const entityGroups = [
  {
    key: 'IDENTITY',
    label: 'Identity',
    items: [
      { key: 'PERSON', label: 'People' },
      { key: 'ORG', label: 'Organisation' },
      { key: 'USERNAME', label: 'Username' },
    ],
  },
  {
    key: 'CONTACT',
    label: 'Contact',
    items: [
      { key: 'EMAIL', label: 'Email' },
      { key: 'PHONE', label: 'Phone' },
      { key: 'ADDRESS', label: 'Address' },
    ],
  },
  {
    key: 'SECURITY',
    label: 'Security',
    items: [
      { key: 'API_KEY', label: 'API key' },
      { key: 'PRIVATE_KEY', label: 'Private key' },
      { key: 'IP_ADDRESS', label: 'IP address' },
    ],
  },
  {
    key: 'FINANCIAL',
    label: 'Financial',
    items: [
      { key: 'CREDIT_CARD', label: 'Credit card' },
      { key: 'BANK_ACCOUNT', label: 'Bank account' },
      { key: 'GOVERNMENT_ID', label: 'Government ID' },
    ],
  },
  {
    key: 'TECHNICAL',
    label: 'Technical',
    items: [
      { key: 'URL', label: 'URL' },
      { key: 'FILE_PATH', label: 'File path' },
      { key: 'COORDINATE', label: 'Coordinate' },
    ],
  },
  {
    key: 'METADATA',
    label: 'Metadata',
    items: [
      { key: 'DATE', label: 'Date' },
      { key: 'COMPANY_REGISTRATION_NUMBER', label: 'Company reg number' },
      { key: 'BOOKING_REFERENCE', label: 'Booking reference' },
      { key: 'TICKET_REFERENCE', label: 'Ticket reference' },
      { key: 'ORDER_ID', label: 'Order ID' },
      { key: 'TRANSACTION_ID', label: 'Transaction ID' },
    ],
  },
]
const allEntityKeys = entityGroups.flatMap((group) => group.items.map((item) => item.key))
const enabled = ref(new Set(DEFAULT_ENTITY_KEYS))

const selectedTypes = computed(() => Array.from(enabled.value))
const charCountLabel = computed(() => `${text.value.length.toLocaleString()} / ${MAX_CHARS.toLocaleString()}`)
const activeEntityTypes = computed(() => (protectAllSensitive.value ? allEntityKeys : selectedTypes.value))
const canSubmit = computed(() => text.value.trim().length > 0 && !loading.value && activeEntityTypes.value.length > 0)
const showExample = computed(() => text.value.trim().length === 0)
const resultWarning = computed(() => result.value?.warning || '')
const resultLanguageLabel = computed(() => {
  const raw = String(result.value?.meta?.language || result.value?.meta?.detected_language || '').trim()
  if (!raw || raw.toLowerCase() === 'unknown') {
    return 'Unknown (English recommended)'
  }
  return raw
})

const resultTotalEntities = computed<number>(() => {
  const counts = (result.value?.counts || {}) as Record<string, number | string | null | undefined>
  let total = 0
  for (const value of Object.values(counts)) {
    total += Number(value ?? 0)
  }
  return total
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
      .replace(/\[(?:🔑\s*)?API Key\s+(\d+)\]/g, '🔑 API Key $1')
      .replace(/\[(?:🔐\s*)?Private Key\s+(\d+)\]/g, '🔐 Private Key $1')
      .replace(/\[(?:🪪\s*)?Government ID\s+(\d+)\]/g, '🪪 Government ID $1')
      .replace(/\[(?:🏦\s*)?Bank Account\s+(\d+)\]/g, '🏦 Bank Account $1')
      .replace(/\[(?:💳\s*)?Credit Card\s+(\d+)\]/g, '💳 Credit Card $1')
      .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, '📞 Phone $1')
      .replace(/\[(?:🌐\s*)?IP Address\s+(\d+)\]/g, '🌐 IP Address $1')
      .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, '🔗 Web Address $1')
      .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, '📍 Location $1')
      .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, '🏢 Organisation $1')
      .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, '📅 Date $1')
      .replace(/\[(?:🏷\s*)?Username\s+(\d+)\]/g, '🏷 Username $1')
      .replace(/\[(?:🧭\s*)?Coordinate\s+(\d+)\]/g, '🧭 Coordinate $1')
      .replace(/\[(?:🗂\s*)?File Path\s+(\d+)\]/g, '🗂 File Path $1')
      .replace(/\b(👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\2\s+(\d+)\b/g, '$1 $2 $3')
  }
  return raw
    .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, 'Person $1')
    .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, 'Email $1')
    .replace(/\[(?:🔑\s*)?API Key\s+(\d+)\]/g, 'API Key $1')
    .replace(/\[(?:🔐\s*)?Private Key\s+(\d+)\]/g, 'Private Key $1')
    .replace(/\[(?:🪪\s*)?Government ID\s+(\d+)\]/g, 'Government ID $1')
    .replace(/\[(?:🏦\s*)?Bank Account\s+(\d+)\]/g, 'Bank Account $1')
    .replace(/\[(?:💳\s*)?Credit Card\s+(\d+)\]/g, 'Credit Card $1')
    .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, 'Phone $1')
    .replace(/\[(?:🌐\s*)?IP Address\s+(\d+)\]/g, 'IP Address $1')
    .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, 'Web Address $1')
    .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, 'Location $1')
    .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, 'Organisation $1')
    .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, 'Date $1')
    .replace(/\[(?:🏷\s*)?Username\s+(\d+)\]/g, 'Username $1')
    .replace(/\[(?:🧭\s*)?Coordinate\s+(\d+)\]/g, 'Coordinate $1')
    .replace(/\[(?:🗂\s*)?File Path\s+(\d+)\]/g, 'File Path $1')
    .replace(/\b(Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\1\s+(\d+)\b/g, '$1 $2')
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
  const tokenPattern = /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|\[REDACTED\])/g

  if (!highlightCensored.value) {
    return escaped
  }

  return escaped.replace(tokenPattern, (token) => {
    const key = normalizeTokenKey(token)
    const tooltip = redactionMode.value ? '' : tokenTooltipMap.value.get(key) || ''
    const tooltipAttr = tooltip ? ` title="${escapeHtml(`Original: ${tooltip}`)}"` : ''
    return `<mark class="sanitise-app__token-highlight"${tooltipAttr}>${token}</mark>`
  })
})

function normalizeTokenKey(token) {
  const cleaned = String(token || '')
    .replace(/\[|\]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^(👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s*/, '')
  return cleaned.toLowerCase()
}

function tokenKeysFromReplacement(replacement) {
  const forms = new Set()
  const raw = String(replacement || '').trim()
  const clean = raw.replace(/^\[|\]$/g, '').trim()
  const plain = clean.replace(/^(👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s*/, '')

  const addForm = (value) => {
    const key = normalizeTokenKey(value)
    if (key) forms.add(key)
  }

  addForm(raw)
  addForm(clean)
  addForm(plain)
  addForm(`[${plain}]`)

  const parsed = plain.match(/^(Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+(\d+)$/i)
  if (parsed) {
    const label = parsed[1]
    const number = parsed[2]
    const emojiByLabel = {
      person: '👤',
      email: '📧',
      'api key': '🔑',
      'private key': '🔐',
      'government id': '🪪',
      'bank account': '🏦',
      'credit card': '💳',
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
    /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b)/g,
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
  if (protectAllSensitive.value) {
    protectAllSensitive.value = false
    allEntityKeys.forEach((typeKey) => current.add(typeKey))
  }
  if (current.has(key)) {
    if (current.size === 1) return
    current.delete(key)
  } else {
    current.add(key)
  }
  enabled.value = current
}

function toggleProtectAllSensitive() {
  protectAllSensitive.value = !protectAllSensitive.value
}

function clearInputText() {
  text.value = ''
  uploadStatus.value = ''
  error.value = ''
  window.requestAnimationFrame(() => {
    inputArea.value?.focus({ preventScroll: true })
  })
}

function handleInputKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    anonymize()
  }
}

async function anonymize() {
  if (!canSubmit.value) return
  submitGlow.value = true
  window.setTimeout(() => {
    submitGlow.value = false
  }, 150)
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
        entity_types: activeEntityTypes.value,
        tag_style: emojiTags.value ? 'emoji' : 'standard',
        reversePronouns: reversePronouns.value,
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
  try {
    const saved = JSON.parse(window.localStorage.getItem(ENTITY_PREFS_KEY) || '{}')
    if (Array.isArray(saved)) {
      const valid = saved.filter((key) => allEntityKeys.includes(key))
      if (valid.length > 0) {
        enabled.value = new Set(valid)
        protectAllSensitive.value = false
      }
    } else if (saved && typeof saved === 'object') {
      if (typeof saved.protect_all === 'boolean') {
        protectAllSensitive.value = saved.protect_all
      }
      if (Array.isArray(saved.selected)) {
        const valid = saved.selected.filter((key) => allEntityKeys.includes(key))
        if (valid.length > 0) {
          enabled.value = new Set(valid)
        }
      }
      if (typeof saved.emoji_tags === 'boolean') {
        emojiTags.value = saved.emoji_tags
      }
      if (typeof saved.reverse_pronouns === 'boolean') {
        reversePronouns.value = saved.reverse_pronouns
      }
      if (typeof saved.redaction_mode === 'boolean') {
        redactionMode.value = saved.redaction_mode
      }
      if (typeof saved.highlight_censored === 'boolean') {
        highlightCensored.value = saved.highlight_censored
      }
    }
  } catch (_) {
    // Ignore invalid saved preferences.
  }

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

watch(
  [protectAllSensitive, enabled, emojiTags, reversePronouns, redactionMode, highlightCensored],
  ([protectAll, selected, emoji, pronouns, redaction, highlight]) => {
    try {
      window.localStorage.setItem(ENTITY_PREFS_KEY, JSON.stringify({
        protect_all: Boolean(protectAll),
        selected: Array.from(selected),
        emoji_tags: Boolean(emoji),
        reverse_pronouns: Boolean(pronouns),
        redaction_mode: Boolean(redaction),
        highlight_censored: Boolean(highlight),
      }))
    } catch (_) {
      // Ignore storage errors (private mode/quota).
    }
  },
  { deep: false }
)
</script>

<template>
  <div class="matrix-bg" aria-hidden="true"></div>
  <main class="sanitise-app">
    <header class="sanitise-app__hero">
      <p class="sanitise-app__brand">Sanitise AI</p>
      <h1 class="sanitise-app__headline sanitise-app__headline--gradient">Sanitise Sensitive Text Before Sending It to AI</h1>
      <div class="sanitise-app__hero-logo-frame" aria-hidden="true">
        <img class="sanitise-app__hero-logo" src="/sanitise-ai-logo-trimmed.png" alt="Sanitise AI logo" />
      </div>
      <p class="sanitise-app__subtitle">Automatically detect and anonymise names, emails, phone numbers and addresses before sharing text with AI tools.</p>
    </header>

    <section class="sanitise-app__composer">
      <div class="sanitise-app__input-header">
        <label for="input" class="sanitise-app__label">Paste sensitive content</label>
        <label for="file-upload" class="sanitise-app__btn sanitise-app__upload-btn">
          {{ fileBusy ? 'Reading file...' : 'Upload PDF or text' }}
        </label>
        <input
          id="file-upload"
          class="sanitise-app__file-input"
          type="file"
          accept=".pdf,.txt,.md,.csv,.json,.log,text/plain,application/pdf,application/json"
          :disabled="fileBusy || loading"
          @change="handleFileSelect"
        />
      </div>
      <p v-if="uploadStatus" class="sanitise-app__charline">{{ uploadStatus }}</p>
      <div class="sanitise-app__input-wrap">
        <div
          :class="['sanitise-app__drop-zone', { 'sanitise-app__drop-zone--active': dropActive }]"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
        >
          <textarea
            id="input"
            ref="inputArea"
            :class="['sanitise-app__textarea', { 'sanitise-app__textarea--highlighted': inputHighlighted }]"
            v-model="text"
            rows="10"
            maxlength="5000"
            placeholder="Paste or drop text or documents here"
            @keydown="handleInputKeydown"
          ></textarea>
          <div class="sanitise-app__charline sanitise-app__charline--inside">{{ charCountLabel }}</div>
        </div>
      </div>
      <section class="sanitise-app__settings">
        <div class="sanitise-app__mode-selector" role="radiogroup" aria-label="Detection mode">
          <label class="sanitise-app__mode-option">
            <input
              type="radio"
              name="detection-mode"
              :checked="protectAllSensitive"
              @change="!protectAllSensitive && toggleProtectAllSensitive()"
            />
            <span class="sanitise-app__mode-dot" aria-hidden="true"></span>
            <span>Automatic (recommended)</span>
          </label>
          <label class="sanitise-app__mode-option">
            <input
              type="radio"
              name="detection-mode"
              :checked="!protectAllSensitive"
              @change="protectAllSensitive && toggleProtectAllSensitive()"
            />
            <span class="sanitise-app__mode-dot" aria-hidden="true"></span>
            <span>Custom rules</span>
          </label>
        </div>
        <div class="sanitise-app__actions sanitise-app__actions--primary">
          <button
            type="button"
            class="sanitise-app__btn sanitise-app__btn--link"
            :disabled="loading || (!text && !uploadStatus)"
            @click="clearInputText"
          >
            Clear
          </button>
          <button
            type="button"
            :class="['sanitise-app__btn', 'sanitise-app__btn--primary', { 'sanitise-app__btn--glowing': submitGlow }]"
            :disabled="!canSubmit"
            @click="anonymize"
          >
            {{ loading ? 'Processing...' : 'Sanitise Text' }}
          </button>
        </div>
      </section>

      <div v-if="!protectAllSensitive" class="sanitise-app__entity-filter">
        <div class="sanitise-app__advanced-groups">
          <section v-for="group in entityGroups" :key="group.key" class="sanitise-app__entity-group">
            <p class="sanitise-app__entity-group-title">{{ group.label }}</p>
            <div class="sanitise-app__toggles sanitise-app__toggles--grouped">
              <button
                v-for="item in group.items"
                :key="item.key"
                type="button"
                :class="['sanitise-app__chip', { 'sanitise-app__chip--active': enabled.has(item.key) }]"
                @click="toggleType(item.key)"
              >
                {{ item.label }}
              </button>
            </div>
          </section>
        </div>
      </div>

      <section class="sanitise-app__transform">
        <p class="sanitise-app__section-title">Optional Transformations</p>
      </section>
      <div class="sanitise-app__option-row">
        <label class="sanitise-app__option">
          <input v-model="emojiTags" type="checkbox" />
          Tag detected entities with emojis
        </label>
        <label class="sanitise-app__option">
          <input v-model="reversePronouns" type="checkbox" />
          Reverse pronouns for anonymisation
        </label>
        <label class="sanitise-app__option">
          <input v-model="redactionMode" type="checkbox" />
          Replace personal data with [REDACTED]
        </label>
      </div>
      <section v-if="showExample" class="sanitise-app__example" aria-label="Example">
        <p class="sanitise-app__section-title">Example</p>
        <div class="sanitise-app__example-grid">
          <div>
            <p class="sanitise-app__example-label">Input</p>
            <p class="sanitise-app__example-copy">John Smith lives at 24 Oxford Street. Email john@gmail.com</p>
          </div>
          <div>
            <p class="sanitise-app__example-label">Output</p>
            <p class="sanitise-app__example-copy">[NAME] lives at [ADDRESS]. Email [EMAIL]</p>
          </div>
        </div>
      </section>
      <div v-if="limitState" class="sanitise-app__limit-card" role="status" aria-live="polite">
        <p class="sanitise-app__limit-title">{{ limitState.message }}</p>
        <p class="sanitise-app__limit-copy">{{ limitState.used }}/{{ limitState.limit }} free anonymisations used today.</p>
        <div class="sanitise-app__actions sanitise-app__actions--limit">
          <button type="button" class="sanitise-app__btn sanitise-app__btn--primary" @click="upgrade">Go Pro</button>
          <button type="button" class="sanitise-app__btn" @click="limitState = null">Dismiss</button>
        </div>
      </div>
      <p v-if="error" class="sanitise-app__error">{{ error }}</p>
    </section>

    <section v-if="result" ref="resultSection" class="sanitise-app__result-grid">
      <div v-if="resultWarning" class="sanitise-app__warning-banner" role="status" aria-live="polite">
        ⚠ {{ resultWarning }}
      </div>
      <article class="sanitise-app__panel">
        <div class="sanitise-app__panel-title-row">
          <h2>Original</h2>
        </div>
        <pre class="sanitise-app__text-block">{{ text }}</pre>
      </article>
      <article class="sanitise-app__panel sanitise-app__panel--anonymised">
        <div class="sanitise-app__panel-title-row">
          <h2>Anonymised</h2>
          <button type="button" class="sanitise-app__btn sanitise-app__btn--compact" @click="copyOutput">{{ copyFeedback }}</button>
        </div>
        <pre class="sanitise-app__text-block" v-html="anonymizedRenderHtml"></pre>
        <div class="sanitise-app__option-row">
          <label class="sanitise-app__option">
            <input v-model="highlightCensored" type="checkbox" />
            Highlight
          </label>
          <label class="sanitise-app__option">
            <input v-model="emojiTags" type="checkbox" />
            Emoji
          </label>
          <label class="sanitise-app__option">
            <input v-model="redactionMode" type="checkbox" />
            Redact
          </label>
        </div>
        <p v-if="resultTotalEntities > 0" class="sanitise-app__success-indicator">✓ {{ resultTotalEntities }} {{ resultTotalEntities === 1 ? 'entity' : 'entities' }} anonymised</p>
        <div v-else class="sanitise-app__no-sensitive-warning" role="status" aria-live="polite">
          <p class="sanitise-app__no-sensitive-note">⚠ No sensitive entities detected. Your text was not changed.</p>
          <p class="sanitise-app__no-sensitive-hint">Try Custom rules if you want stricter matching.</p>
        </div>
        <div class="sanitise-app__actions">
          <button type="button" class="sanitise-app__btn" @click="downloadOutput">Download .txt</button>
        </div>
      </article>
    </section>

    <section v-if="result" class="sanitise-app__meta-section">
      <h2>Detection Summary</h2>
      <p class="sanitise-app__meta-line">{{ summaryLine }}</p>
      <div class="sanitise-app__counts">
        <span v-for="(count, key) in result.counts" :key="key" class="sanitise-app__count-item">{{ key }}: {{ count }}</span>
      </div>
      <div class="sanitise-app__actions">
        <button type="button" class="sanitise-app__btn" @click="upgrade">Advanced export features</button>
      </div>
    </section>

    <section v-if="result?.cta_visaprep" class="sanitise-app__meta-section sanitise-app__meta-section--cta">
      <h2>Need immigration-specific help next?</h2>
      <p>Your text looks immigration-related. You can continue safely with redacted content on Visaprep.</p>
      <a href="https://visaprep.uk" target="_blank" rel="noreferrer" class="sanitise-app__btn sanitise-app__btn--primary">Open Visaprep</a>
    </section>

    <footer class="sanitise-app__footer">
      <p>Built by Nima Parsi</p>
      <p><a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">Open source on GitHub</a></p>
      <p><a href="/privacy.html">Privacy policy</a></p>
      <p>No data stored</p>
      <p>Sensitive data is anonymised before any AI processing.</p>
      <p class="sanitise-app__engine-credit">Powered by the Matrix Privacy Engine</p>
    </footer>
  </main>
</template>

<style lang="scss" src="./global.scss"></style>
<style scoped lang="scss" src="./App.scss"></style>
