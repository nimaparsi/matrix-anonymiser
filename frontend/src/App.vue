<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const MAX_CHARS = 50000
const MAX_UPLOAD_BYTES = 8 * 1024 * 1024
const TEXT_EXTENSIONS = new Set(['txt', 'md', 'csv', 'json', 'log'])
let pdfRuntimePromise = null

function apiUrl(path) {
  const base = API_BASE.replace(/\/$/, '')
  return base ? `${base}/api/${path}` : `/api/${path}`
}

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const emojiTags = ref(false)
const highlightCensored = ref(true)
const resultSection = ref(null)
const inputArea = ref(null)
const inputHighlighted = ref(false)
const fileBusy = ref(false)
const uploadStatus = ref('')

const entityOptions = [
  { key: 'PERSON', label: 'Person' },
  { key: 'EMAIL', label: 'Email' },
  { key: 'PHONE', label: 'Phone' },
  { key: 'URL', label: 'Web address' },
  { key: 'ADDRESS', label: 'Address' },
  { key: 'ORG', label: 'Organisation' },
  { key: 'DATE', label: 'Date' }
]
const allEntityKeys = entityOptions.map((item) => item.key)

const enabled = ref(new Set(['PERSON', 'EMAIL', 'PHONE', 'URL', 'ADDRESS', 'ORG']))

const selectedTypes = computed(() => Array.from(enabled.value))
const charsLeft = computed(() => MAX_CHARS - text.value.length)
const canSubmit = computed(() => text.value.trim().length > 0 && !loading.value && selectedTypes.value.length > 0)
const allEnabled = computed(() => allEntityKeys.every((key) => enabled.value.has(key)))
const displayAnonymizedText = computed(() => {
  const raw = result.value?.anonymized_text || ''
  return raw
    .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, 'Person $1')
    .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, 'Email $1')
    .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, 'Phone $1')
    .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, 'Web Address $1')
    .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, 'Location $1')
    .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, 'Organisation $1')
    .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, 'Date $1')
    .replace(/\b(Person|Email|Phone|Web Address|Location|Organisation|Date)\s+\1\s+(\d+)\b/g, '$1 $2')
})

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const anonymizedRenderHtml = computed(() => {
  const escaped = escapeHtml(displayAnonymizedText.value)
  if (!highlightCensored.value) return escaped
  const tokenPattern = /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|Phone|Web Address|Location|Organisation|Date)\s+\d+\b)/g
  return escaped.replace(tokenPattern, '<mark class=\"token-highlight\">$1</mark>')
})

function toggleType(key) {
  const current = new Set(enabled.value)
  if (current.has(key)) {
    current.delete(key)
  } else {
    current.add(key)
  }
  enabled.value = current
}

function handleEmojiToggle() {
  if (!result.value || loading.value) return
  anonymize()
}

function toggleAllTypes() {
  if (allEnabled.value) {
    enabled.value = new Set()
    return
  }
  enabled.value = new Set(allEntityKeys)
}

async function anonymize() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''
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
      })
    })

    const data = await res.json()
    if (!res.ok) {
      const detail = typeof data.detail === 'string' ? data.detail : data.detail?.message || 'Anonymisation failed'
      throw new Error(detail)
    }

    result.value = data
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
    const content = await page.getTextContent()
    const pageText = content.items
      .map((item) => ('str' in item ? item.str : ''))
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim()
    pages.push(pageText)
  }
  return pages.join('\n\n')
}

function normalizeLoadedText(raw) {
  return String(raw || '').replace(/\u0000/g, '').trim()
}

async function handleFileSelect(event) {
  const input = event.target
  const file = input.files?.[0]
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
    input.value = ''
  }
}

async function copyOutput() {
  if (!result.value?.anonymized_text) return
  await navigator.clipboard.writeText(result.value.anonymized_text)
}

function downloadOutput() {
  if (!result.value?.anonymized_text) return
  const blob = new Blob([result.value.anonymized_text], { type: 'text/plain;charset=utf-8' })
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
        <img class="brand-icon" src="/favicon.svg" alt="Matrix Anonymiser icon" />
        <h1>Sanitise text before AI sees it.</h1>
      </div>
      <p class="subtitle">Turn sensitive text into safe-to-share content in seconds.</p>
      <p class="subtitle">Built for documents, case notes, logs, and AI prompts.</p>
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
        <span class="upload-note">Parsed locally in your browser</span>
      </div>
      <p v-if="uploadStatus" class="charline">{{ uploadStatus }}</p>
      <textarea id="input" ref="inputArea" :class="{ 'load-highlight': inputHighlighted }" v-model="text" rows="10" maxlength="50000" placeholder="Paste personal or sensitive text here..."></textarea>
      <div class="charline">{{ charsLeft }} characters remaining</div>

      <div class="toggles">
        <button
          type="button"
          :class="['chip', { active: allEnabled }]"
          @click="toggleAllTypes"
        >
          All
        </button>
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

      <div class="actions">
        <button type="button" class="btn primary" :disabled="!canSubmit" @click="anonymize">
          {{ loading ? 'Processing...' : 'Anonymise' }}
        </button>
        <button type="button" class="btn" @click="upgrade">Upgrade to Pro</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section v-if="result" ref="resultSection" class="grid">
      <article class="panel">
        <h2>Original</h2>
        <pre>{{ text }}</pre>
      </article>
      <article class="panel">
        <h2>Anonymised</h2>
        <label class="friendly-option">
          <input v-model="emojiTags" type="checkbox" :disabled="loading" @change="handleEmojiToggle" />
          Emoji tags
        </label>
        <label class="friendly-option">
          <input v-model="highlightCensored" type="checkbox" />
          Highlight censored words
        </label>
        <pre v-html="anonymizedRenderHtml"></pre>
        <div class="actions">
          <button type="button" class="btn" @click="copyOutput">Copy</button>
          <button type="button" class="btn" @click="downloadOutput">Download .txt</button>
        </div>
      </article>
    </section>

    <section v-if="result" class="panel">
      <h2>Detection Summary</h2>
      <p class="meta">{{ result.meta?.processing_ms }}ms · Tier: {{ result.meta?.tier }} · Usage: {{ result.meta?.usage_used }}/{{ result.meta?.usage_limit }}</p>
      <div class="counts">
        <span v-for="(count, key) in result.counts" :key="key" class="count-item">{{ key }}: {{ count }}</span>
      </div>
    </section>

    <section v-if="result?.cta_visaprep" class="panel cta">
      <h2>Need immigration-specific help next?</h2>
      <p>Your text looks immigration-related. You can continue safely with redacted content on Visaprep.</p>
      <a href="https://visaprep.uk" target="_blank" rel="noreferrer" class="btn primary">Open Visaprep</a>
    </section>

    <footer class="site-footer">
      Made by Nima Parsi ·
      <a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">
        Open source on GitHub
      </a> ·
      <a href="/privacy.html">Privacy</a>
    </footer>
  </main>
</template>
