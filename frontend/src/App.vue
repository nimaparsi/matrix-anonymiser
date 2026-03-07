<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''

function apiUrl(path) {
  const base = API_BASE.replace(/\/$/, '')
  return base ? `${base}/api/${path}` : `/api/${path}`
}

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const emojiTags = ref(false)
const readableOutput = ref(true)
const resultSection = ref(null)

const entityOptions = [
  { key: 'PERSON', label: 'Person' },
  { key: 'EMAIL', label: 'Email' },
  { key: 'PHONE', label: 'Phone' },
  { key: 'ADDRESS', label: 'Address' },
  { key: 'ORG', label: 'Organisation' },
  { key: 'DATE', label: 'Date' }
]

const enabled = ref(new Set(['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG']))

const selectedTypes = computed(() => Array.from(enabled.value))
const charsLeft = computed(() => 50000 - text.value.length)
const canSubmit = computed(() => text.value.trim().length > 0 && !loading.value && selectedTypes.value.length > 0)
const displayAnonymizedText = computed(() => {
  const raw = result.value?.anonymized_text || ''
  if (!readableOutput.value) return raw
  return raw
    .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, 'Person $1')
    .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, 'Email $1')
    .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, 'Phone $1')
    .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, 'Location $1')
    .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, 'Organisation $1')
    .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, 'Date $1')
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
  const sessionId = new URLSearchParams(window.location.search).get('session_id')
  if (!sessionId) return
  try {
    await fetch(`${apiUrl('billing/activate')}?session_id=${encodeURIComponent(sessionId)}`, {
      credentials: 'include'
    })
  } catch (_) {
    // Do not block normal app usage if billing activation fails.
  }
})
</script>

<template>
  <div class="matrix-bg" aria-hidden="true"></div>
  <main class="container">
    <header class="hero">
      <p class="eyebrow">Matrix Privacy Engine</p>
      <h1>Sanitise text before AI sees it.</h1>
      <p class="subtitle">No storage. Transient processing. Redacted telemetry.</p>
      <p class="subtitle"><a class="privacy-link" href="/privacy.html" target="_blank" rel="noreferrer">Privacy policy</a></p>
      <div class="trust-row">
        <span>No storage</span>
        <span>Processed transiently</span>
        <span>Logs redacted</span>
      </div>
    </header>

    <section class="panel">
      <label for="input" class="label">Paste text</label>
      <textarea id="input" v-model="text" rows="10" maxlength="50000" placeholder="Paste personal or sensitive text here..."></textarea>
      <div class="charline">{{ charsLeft }} characters remaining</div>

      <div class="toggles">
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
      <label class="friendly-option">
        <input v-model="emojiTags" type="checkbox" />
        Friendly emoji tags
      </label>

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
          <input v-model="readableOutput" type="checkbox" />
          Readable output
        </label>
        <pre>{{ displayAnonymizedText }}</pre>
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
      </a>
    </footer>
  </main>
</template>
