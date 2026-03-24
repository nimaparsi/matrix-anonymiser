<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { PhArrowsLeftRight, PhClipboardText, PhCopySimple, PhSparkle } from '@phosphor-icons/vue'

type TokenType = 'Person' | 'Organisation' | 'Email' | 'Phone' | 'Address' | 'ApiKey' | 'IpAddress'
type TagOption = {
  key: TokenType
  label: string
  hint: string
  icon: string
}

type TryExampleEvent = CustomEvent<{
  useCase?: string
  quickStart?: boolean
  text?: string
  focus?: boolean
}>

type OutputPart = {
  text: string
  tokenType?: TokenType
}

const TOKEN_PATTERN = /\[(Person|Organisation|Email|Phone|Address|ApiKey|IpAddress)\s+(\d+)\]/g
const TAG_TO_BACKEND_ENTITY: Record<TokenType, string> = {
  Person: 'PERSON',
  Organisation: 'ORG',
  Email: 'EMAIL',
  Phone: 'PHONE',
  Address: 'ADDRESS',
  ApiKey: 'API_KEY',
  IpAddress: 'IP_ADDRESS',
}
const BACKEND_TOKEN_TO_UI: Record<string, TokenType> = {
  PERSON: 'Person',
  ORGANISATION: 'Organisation',
  ORGANIZATION: 'Organisation',
  ORG: 'Organisation',
  EMAIL: 'Email',
  PHONE: 'Phone',
  ADDRESS: 'Address',
  LOCATION: 'Address',
  'API KEY': 'ApiKey',
  APIKEY: 'ApiKey',
  API_KEY: 'ApiKey',
  'IP ADDRESS': 'IpAddress',
  IPADDRESS: 'IpAddress',
  IP_ADDRESS: 'IpAddress',
}

const inputText = ref('')
const outputText = ref('')
const copyLabel = ref('Copy output')
const statusMessage = ref('')
const isSanitising = ref(false)
const outputPulse = ref(false)
const lastSanitisedSignature = ref<string | null>(null)
const detectionMode = ref<'automatic' | 'custom'>('automatic')
const selectedTagKeys = ref<TokenType[]>(['Person', 'Organisation', 'Email', 'Phone', 'Address'])
const reversePronounsEnabled = ref(false)
const inputEl = ref<HTMLTextAreaElement | null>(null)
const detectedCount = ref(0)
const detectedLabels = ref<string[]>([])

let statusTimer: ReturnType<typeof window.setTimeout> | null = null
let sanitiseTimer: ReturnType<typeof window.setTimeout> | null = null
let pulseTimer: ReturnType<typeof window.setTimeout> | null = null

const MIN_TEXTAREA_HEIGHT = 210
const TEXTAREA_VIEWPORT_OFFSET = 350
const TEXTAREA_MAX_HARD_CAP = 500
const SANITISE_SPINNER_MS = 320

const tagOptions: TagOption[] = [
  { key: 'Person', label: 'People', hint: 'Names', icon: '👤' },
  { key: 'Organisation', label: 'Organisation', hint: 'Companies', icon: '🏢' },
  { key: 'Email', label: 'Email', hint: 'Addresses', icon: '📧' },
  { key: 'Phone', label: 'Phone', hint: 'Numbers', icon: '📞' },
  { key: 'Address', label: 'Address', hint: 'Locations', icon: '📍' },
  { key: 'ApiKey', label: 'API keys', hint: 'Secrets', icon: '🔐' },
  { key: 'IpAddress', label: 'IP address', hint: 'Hosts', icon: '🌐' },
]

const defaultExampleText = [
  'John Smith from Acme emailed john@acme.com.',
  'Call me on 07912345678 about the contract update.',
].join('\n')

const generalExamples = [
  [
    'NHS referral note',
    'Patient: Eleanor Matthews (DOB: 14/02/1988)',
    'NHS no: 943 476 1820',
    'Consultant: Dr James Holloway',
    'Email: james.holloway@westbrook-hospital.nhs.uk',
    'Phone: +44 7700 901144',
    'Address: 43 Hawthorn Road, Leeds LS7 2AA',
    'Discharge follow-up booked for 29 March 2026.',
  ].join('\n'),
  [
    'Production auth incident - API gateway',
    'Owner: Alice Morgan',
    'GitHub user: alice-morgan-dev',
    'Email: alice.morgan@contoso.dev',
    'Pager: +44 7700 900456',
    'Host: 10.12.8.32',
    'GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH8G2Ud4h6ZcF1b8Q8kTWX5q2e4w9rjQ7w2L2N2 alice@contoso',
    'Access token: ghp_u7QxY3nN9aK1dL4mZ8tW2pR6hC0vB5e',
  ].join('\n'),
  [
    'MSA amendment summary',
    'Client: BrightEdge Consulting Ltd',
    'Legal contact: Sarah Thompson',
    'Email: sarah.thompson@brightedge.co.uk',
    'Phone: +44 7700 900123',
    'Registered office: 1 Finsbury Square, London EC2A 1AE',
    'Invoice #: INV-88421',
    'Jurisdiction: England and Wales',
  ].join('\n'),
  [
    'Project coordination memo',
    'Prepared by: Anna Carter',
    'Organisation: Green Horizon Research',
    'Contact: anna.carter@example.com',
    'Phone: +44 7700 900123',
    'Address: 14 Willow Lane, Brighton BN1 4AB',
    'Attendees: Daniel Hughes, Sofia Martinez, Ravi Patel',
  ].join('\n'),
  [
    'Recruiter interview debrief',
    'Candidate: Daniel Hughes',
    'Email: daniel.hughes@careersmail.com',
    'Mobile: 07912 123456',
    'Current employer: Green Horizon Research',
    'Home address: 21 Cedar Avenue, Manchester M3 1AA',
    'Referee: Laura Chen (laura.chen@urbanlabs.co.uk)',
  ].join('\n'),
  defaultExampleText,
]

let generalExampleCursor = -1

const useCaseExamples: Record<string, string> = {
  Developers: [
    'GitHub production incident ticket',
    'Reporter: Alice Morgan',
    'Email: alice.morgan@contoso.dev',
    'Phone: +44 7700 900456',
    'Host: 10.12.8.32',
    'GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFl2dD9pQm7rX4uN8wE1yT5kL3cB6vR2pH0sJ9n alice@contoso-dev',
    'Service API key: api_key=prod_9fH3mQ7xV2pL5rT8kN1dW4cY',
  ].join('\n'),
  Recruiters: [
    'Candidate profile summary',
    'Name: Daniel Hughes',
    'Email: daniel.hughes@careersmail.com',
    'Phone: 07912 123456',
    'Address: 21 Cedar Avenue, Manchester',
    'Current employer: Green Horizon Research',
  ].join('\n'),
  Consultants: [
    'Client workshop prep memo',
    'Prepared for: Sofia Martinez',
    'Contact: sofia.martinez@clientgroup.co.uk',
    'Mobile: +44 7700 903876',
    'Office: 14 Willow Lane, Brighton',
    'Organisation: Urban Growth Initiative',
  ].join('\n'),
  Students: [
    'Coursework submission context',
    'Student: Ravi Patel',
    'University email: ravi.patel@studentmail.ac.uk',
    'Phone: 07700 905112',
    'Placement company: Future Energy Alliance',
    'Reference address: 55 Orchard Street, Manchester',
  ].join('\n'),
}

const hasInput = computed(() => inputText.value.trim().length > 0)
const hasOutput = computed(() => outputText.value.trim().length > 0)

const enabledTagSet = computed(() =>
  detectionMode.value === 'automatic'
    ? new Set<TokenType>(tagOptions.map((tag) => tag.key))
    : new Set<TokenType>(selectedTagKeys.value),
)

const currentSanitiseSignature = computed(() => {
  const enabledTags = [...enabledTagSet.value].sort()
  return `${inputText.value}\u0000${detectionMode.value}\u0000${enabledTags.join('|')}\u0000${reversePronounsEnabled.value}`
})

const needsSanitise = computed(() => {
  if (!hasInput.value) return false
  if (!hasOutput.value) return true
  return currentSanitiseSignature.value !== lastSanitisedSignature.value
})

const modeSummary = computed(() =>
  detectionMode.value === 'automatic' ? 'Automatic detection enabled' : `${selectedTagKeys.value.length} custom rules enabled`,
)

const transformSummary = computed(() => (reversePronounsEnabled.value ? ' · Reverse pronouns on' : ''))

const liveDetectionVisible = computed(() => !needsSanitise.value && detectedCount.value > 0)
const liveDetectionLabels = computed(() => detectedLabels.value.slice(0, 4))

const sanitiseButtonLabel = computed(() => {
  if (isSanitising.value) return 'Sanitising…'
  if (hasInput.value && !needsSanitise.value) return 'Sanitised'
  return 'Sanitise text'
})

const renderedOutputLines = computed(() => {
  if (!outputText.value) return [] as OutputPart[][]
  return outputText.value.split('\n').map((line) => splitOutputLine(line))
})

function setStatus(message: string, timeout = 2200) {
  statusMessage.value = message
  if (statusTimer) window.clearTimeout(statusTimer)
  statusTimer = window.setTimeout(() => {
    statusMessage.value = ''
    statusTimer = null
  }, timeout)
}

function canonicalizeBackendTokens(value: string) {
  if (!value) return ''
  const normalizeLabel = (label: string) => label.trim().replace(/\s+/g, ' ').replace(/[_-]+/g, '_').toUpperCase()

  const convertedUnderscore = value.replace(/\[([A-Z_]+)_(\d+)\]/g, (full, rawLabel: string, index: string) => {
    const normalized = normalizeLabel(rawLabel)
    const mapped = BACKEND_TOKEN_TO_UI[normalized]
    return mapped ? `[${mapped} ${index}]` : full
  })

  return convertedUnderscore.replace(/\[([A-Za-z][A-Za-z _-]+)\s+(\d+)\]/g, (full, rawLabel: string, index: string) => {
    const normalized = normalizeLabel(rawLabel).replace(/_/g, ' ')
    const mapped = BACKEND_TOKEN_TO_UI[normalized] || BACKEND_TOKEN_TO_UI[normalized.replace(/\s+/g, '')]
    return mapped ? `[${mapped} ${index}]` : full
  })
}

function normalizeBackendEntity(value: string) {
  return value.trim().replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').toUpperCase()
}

function buildDetectionFromCounts(rawCounts: Record<string, unknown> | undefined, fallbackOutput: string) {
  const totals = new Map<TokenType, number>()

  if (rawCounts && typeof rawCounts === 'object') {
    for (const [rawKey, rawValue] of Object.entries(rawCounts)) {
      const count = Number(rawValue)
      if (!Number.isFinite(count) || count <= 0) continue
      const normalized = normalizeBackendEntity(rawKey)
      const mapped =
        BACKEND_TOKEN_TO_UI[normalized] || BACKEND_TOKEN_TO_UI[normalized.replace(/\s+/g, '')] || null
      if (!mapped) continue
      totals.set(mapped, (totals.get(mapped) ?? 0) + count)
    }
  }

  if (totals.size === 0) {
    const fallback = extractTokenStats(fallbackOutput)
    return { count: fallback.total, labels: fallback.previewLabels }
  }

  const ordered = [...totals.entries()].sort((a, b) => b[1] - a[1])
  const labels = ordered.slice(0, 4).map(([type]) => {
    const option = tagOptions.find((tag) => tag.key === type)
    return option?.label ?? type
  })

  const count = ordered.reduce((sum, [, value]) => sum + value, 0)
  return { count, labels }
}

async function anonymiseViaApi(rawText: string, enabledTags: Set<TokenType>, reversePronouns = false) {
  const entity_types = [...enabledTags].map((key) => TAG_TO_BACKEND_ENTITY[key]).filter(Boolean)
  const response = await fetch('/api/anonymize', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      text: rawText,
      entity_types,
      tag_style: 'standard',
      reverse_pronouns: reversePronouns,
    }),
  })
  if (!response.ok) throw new Error(`API ${response.status}`)
  const payload = (await response.json()) as {
    anonymized_text?: string
    counts?: Record<string, unknown>
  }
  const output = canonicalizeBackendTokens(String(payload?.anonymized_text || ''))
  return { output, ...buildDetectionFromCounts(payload?.counts, output) }
}

function extractTokenStats(text: string) {
  const counter = new Map<TokenType, number>()
  let total = 0

  for (const match of text.matchAll(TOKEN_PATTERN)) {
    const tokenType = match[1] as TokenType
    total += 1
    counter.set(tokenType, (counter.get(tokenType) ?? 0) + 1)
  }

  const previewLabels = [...counter.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([type]) => {
      const option = tagOptions.find((tag) => tag.key === type)
      return option?.label ?? type
    })

  return { total, previewLabels }
}

function splitOutputLine(line: string) {
  if (!line) return [{ text: '' }] as OutputPart[]

  const parts: OutputPart[] = []
  TOKEN_PATTERN.lastIndex = 0
  let lastIndex = 0

  for (const match of line.matchAll(TOKEN_PATTERN)) {
    const start = match.index ?? 0
    if (start > lastIndex) {
      parts.push({ text: line.slice(lastIndex, start) })
    }
    parts.push({ text: match[0], tokenType: match[1] as TokenType })
    lastIndex = start + match[0].length
  }

  if (lastIndex < line.length) {
    parts.push({ text: line.slice(lastIndex) })
  }

  return parts.length ? parts : [{ text: line }]
}

function triggerOutputPulse() {
  outputPulse.value = true
  if (pulseTimer) window.clearTimeout(pulseTimer)
  pulseTimer = window.setTimeout(() => {
    outputPulse.value = false
    pulseTimer = null
  }, 360)
}

async function sanitiseNow() {
  if (!hasInput.value || isSanitising.value || !needsSanitise.value) return

  isSanitising.value = true
  const previousOutput = outputText.value
  const previousDetectedCount = detectedCount.value
  const previousDetectedLabels = [...detectedLabels.value]
  outputText.value = ''
  detectedCount.value = 0
  detectedLabels.value = []

  await new Promise<void>((resolve) => {
    sanitiseTimer = window.setTimeout(() => {
      sanitiseTimer = null
      resolve()
    }, SANITISE_SPINNER_MS)
  })

  try {
    const sanitized = await anonymiseViaApi(inputText.value, enabledTagSet.value, reversePronounsEnabled.value)
    outputText.value = sanitized.output
    detectedCount.value = sanitized.count
    detectedLabels.value = sanitized.labels
    lastSanitisedSignature.value = currentSanitiseSignature.value
    copyLabel.value = 'Copy output'
    triggerOutputPulse()
  } catch {
    outputText.value = previousOutput
    detectedCount.value = previousDetectedCount
    detectedLabels.value = previousDetectedLabels
    setStatus('Sanitisation service unavailable. Please try again.')
  }
  isSanitising.value = false
}

function isTagEnabled(key: TokenType) {
  return selectedTagKeys.value.includes(key)
}

function toggleTag(key: TokenType) {
  const hasTag = selectedTagKeys.value.includes(key)
  if (hasTag) {
    if (selectedTagKeys.value.length === 1) {
      setStatus('Keep at least one custom rule active')
      return
    }
    selectedTagKeys.value = selectedTagKeys.value.filter((tag) => tag !== key)
    return
  }
  selectedTagKeys.value = [...selectedTagKeys.value, key]
}

function cancelSanitiseTimer() {
  if (sanitiseTimer) {
    window.clearTimeout(sanitiseTimer)
    sanitiseTimer = null
  }
}

async function focusInputCursor() {
  await nextTick()
  inputEl.value?.focus()
  const len = inputText.value.length
  inputEl.value?.setSelectionRange(len, len)
}

function getTextareaMaxHeight() {
  const viewportHeight = window.innerHeight || 900
  return Math.max(MIN_TEXTAREA_HEIGHT, Math.min(TEXTAREA_MAX_HARD_CAP, viewportHeight - TEXTAREA_VIEWPORT_OFFSET))
}

function syncTextareaHeight() {
  const el = inputEl.value
  if (!el) return

  const maxHeight = getTextareaMaxHeight()
  el.style.height = 'auto'

  const nextHeight = Math.min(Math.max(el.scrollHeight, MIN_TEXTAREA_HEIGHT), maxHeight)
  el.style.height = `${nextHeight}px`
  el.style.overflowY = el.scrollHeight > maxHeight ? 'auto' : 'hidden'
}

function pickExampleText(useCase?: string) {
  if (useCase && useCaseExamples[useCase]) return useCaseExamples[useCase]

  if (generalExamples.length === 0) return defaultExampleText
  generalExampleCursor = (generalExampleCursor + 1) % generalExamples.length
  return generalExamples[generalExampleCursor]
}

async function applyExample(useCase?: string) {
  inputText.value = pickExampleText(useCase)
  await sanitiseNow()
  setStatus('Example loaded')
}

function clearDemo() {
  cancelSanitiseTimer()
  isSanitising.value = false
  inputText.value = ''
  outputText.value = ''
  detectedCount.value = 0
  detectedLabels.value = []
  lastSanitisedSignature.value = null
  copyLabel.value = 'Copy output'
  statusMessage.value = ''
}

async function pasteFromClipboard() {
  try {
    const clipboardText = await navigator.clipboard.readText()
    if (!clipboardText.trim()) {
      setStatus('Clipboard is empty')
      return
    }
    inputText.value = clipboardText
    await sanitiseNow()
    setStatus('Pasted and sanitised')
  } catch {
    setStatus('Clipboard access blocked')
  }
}

async function copyOutput() {
  if (!hasOutput.value) return
  try {
    await navigator.clipboard.writeText(outputText.value)
    copyLabel.value = 'Copied'
    setStatus('Output copied')
    window.setTimeout(() => {
      copyLabel.value = 'Copy output'
    }, 1400)
  } catch {
    setStatus('Copy failed')
  }
}

function runQuickStart() {
  window.dispatchEvent(
    new CustomEvent('sanitiseai:try-example', {
      detail: {
        quickStart: true,
        text: defaultExampleText,
        focus: true,
      },
    }),
  )
}

function handleInputKeydown(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    void sanitiseNow()
  }
}

function handleWindowResize() {
  syncTextareaHeight()
}

function handleTryExampleEvent(event: Event) {
  const customEvent = event as TryExampleEvent
  const detail = customEvent.detail

  if (detail?.quickStart) {
    cancelSanitiseTimer()
    isSanitising.value = false
    inputText.value = detail.text?.trim() ? detail.text : defaultExampleText
    void sanitiseNow()

    if (detail.focus ?? true) {
      void focusInputCursor()
    }
    return
  }

  void applyExample(detail?.useCase)
}

onMounted(() => {
  window.addEventListener('sanitiseai:try-example', handleTryExampleEvent as EventListener)
  window.addEventListener('resize', handleWindowResize)
  void nextTick(syncTextareaHeight)
})

onUnmounted(() => {
  if (statusTimer) {
    window.clearTimeout(statusTimer)
    statusTimer = null
  }
  if (sanitiseTimer) {
    window.clearTimeout(sanitiseTimer)
    sanitiseTimer = null
  }
  if (pulseTimer) {
    window.clearTimeout(pulseTimer)
    pulseTimer = null
  }
  window.removeEventListener('sanitiseai:try-example', handleTryExampleEvent as EventListener)
  window.removeEventListener('resize', handleWindowResize)
})

watch(inputText, () => {
  void nextTick(syncTextareaHeight)
})
</script>

<template>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero__header">
      <div class="hero__copy">
        <p class="hero__eyebrow">PII REDACTION FOR AI • ZERO DATA RETENTION</p>
        <h1 id="hero-title">Protect your data without compromise.</h1>
        <p class="hero__lede">
          The world’s advanced data sanitisation layer. Anonymise sensitive information using our production backend
          before sharing with AI tools, documents, or teammates.
        </p>
        <button class="btn btn--primary hero__try" type="button" @click="runQuickStart">
          <PhSparkle :size="15" weight="fill" aria-hidden="true" />
          <span>Try it free</span>
        </button>
      </div>
      <img class="hero__mascot" src="/sanitise-ai-logo-trimmed.png" alt="SanitiseAI logo" loading="eager" />
    </div>

    <article class="hero__demo" aria-label="Interactive anonymisation demo">
      <header class="hero__demo-head">
        <div>
          <p class="hero__demo-title">See the transformation instantly</p>
          <p class="hero__demo-subtitle">Input text on the left, sanitised output on the right.</p>
        </div>
        <div class="hero__demo-actions">
          <button class="btn btn--secondary" type="button" @click="() => applyExample()">Try example</button>
          <button class="btn btn--ghost" type="button" :disabled="!hasInput || isSanitising" @click="clearDemo">
            Clear
          </button>
        </div>
      </header>

      <div class="hero__demo-grid">
        <section class="hero__panel">
          <div class="hero__panel-top">
            <label class="hero__label" for="demo-input">Original text</label>
            <button class="hero__chip" type="button" @click="pasteFromClipboard">
              <PhClipboardText :size="14" weight="duotone" aria-hidden="true" />
              <span>Paste clipboard</span>
            </button>
          </div>

          <textarea
            id="demo-input"
            ref="inputEl"
            v-model="inputText"
            class="hero__textarea"
            placeholder="Paste text containing sensitive information or drop a document to anonymise"
            @keydown="handleInputKeydown"
          ></textarea>

          <div class="hero__row hero__row--cta">
            <div v-if="liveDetectionVisible" class="hero__live-detect" role="status" aria-live="polite">
              <strong>Sensitive entities detected: {{ detectedCount }}</strong>
              <span>{{ liveDetectionLabels.join(' · ') }}</span>
            </div>

            <button
              class="btn btn--primary hero__sanitise"
              type="button"
              :disabled="!hasInput || isSanitising || !needsSanitise"
              @click="sanitiseNow"
            >
              <PhSparkle :size="14" weight="fill" aria-hidden="true" />
              <span>{{ sanitiseButtonLabel }}</span>
            </button>
          </div>

          <div class="hero__options">
            <div class="hero__mode" role="group" aria-label="Detection mode">
              <button
                type="button"
                class="hero__mode-btn"
                :class="{ 'hero__mode-btn--active': detectionMode === 'automatic' }"
                @click="detectionMode = 'automatic'"
              >
                Automatic (recommended)
              </button>
              <button
                type="button"
                class="hero__mode-btn"
                :class="{ 'hero__mode-btn--active': detectionMode === 'custom' }"
                @click="detectionMode = 'custom'"
              >
                Custom rules
              </button>
            </div>

            <button
              type="button"
              class="hero__transform-toggle"
              :class="{ 'hero__transform-toggle--active': reversePronounsEnabled }"
              @click="reversePronounsEnabled = !reversePronounsEnabled"
            >
              <span class="hero__transform-icon" aria-hidden="true">
                <PhArrowsLeftRight :size="14" weight="bold" />
              </span>
              <span class="hero__transform-copy">
                <span class="hero__transform-label">Reverse pronouns</span>
                <span class="hero__transform-hint">Experimental transformation</span>
              </span>
              <span class="hero__transform-state">{{ reversePronounsEnabled ? 'On' : 'Off' }}</span>
            </button>

            <div v-if="detectionMode === 'custom'" class="hero__tag-grid" aria-live="polite">
              <button
                v-for="tag in tagOptions"
                :key="tag.key"
                type="button"
                class="hero__tag-chip"
                :class="{ 'hero__tag-chip--active': isTagEnabled(tag.key) }"
                @click="toggleTag(tag.key)"
              >
                <span class="hero__tag-icon" aria-hidden="true">{{ tag.icon }}</span>
                <span class="hero__tag-copy">
                  <span class="hero__tag-label">{{ tag.label }}</span>
                  <span class="hero__tag-hint">{{ tag.hint }}</span>
                </span>
              </button>
            </div>
          </div>

          <p v-if="statusMessage" class="hero__status" role="status" aria-live="polite">{{ statusMessage }}</p>
        </section>

        <section class="hero__panel hero__panel--output" :class="{ 'hero__panel--pulse': outputPulse }">
          <div class="hero__panel-top">
            <p class="hero__label">Sanitised output</p>
            <button class="hero__chip" type="button" :disabled="!hasOutput || isSanitising" @click="copyOutput">
              <PhCopySimple :size="14" weight="duotone" aria-hidden="true" />
              <span>{{ copyLabel }}</span>
            </button>
          </div>

          <p class="hero__output-meta">
            {{ modeSummary }}{{ transformSummary }}<span v-if="liveDetectionLabels.length"> · {{ liveDetectionLabels.join(' · ') }}</span>
          </p>

          <div class="hero__output-wrap">
            <div class="hero__output" :class="{ 'hero__output--reveal': outputPulse }">
              <template v-if="renderedOutputLines.length">
                <p v-for="(line, lineIndex) in renderedOutputLines" :key="lineIndex" class="hero__output-line">
                  <template v-for="(part, partIndex) in line" :key="`${lineIndex}-${partIndex}`">
                    <span
                      v-if="part.tokenType"
                      class="hero__token"
                      :class="`hero__token--${part.tokenType.toLowerCase()}`"
                    >
                      {{ part.text }}
                    </span>
                    <span v-else>{{ part.text }}</span>
                  </template>
                </p>
              </template>
              <p v-else class="hero__placeholder">Sanitised output appears here.</p>
            </div>

            <div v-if="isSanitising" class="hero__spinner" role="status" aria-live="polite">
              <span class="hero__spinner-ring" aria-hidden="true"></span>
              <span>Sanitising...</span>
            </div>
          </div>
        </section>
      </div>
    </article>
  </section>
</template>

<style scoped lang="scss">
.hero {
  &__header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 1.2rem;
  }

  &__eyebrow {
    margin: 0;
    color: #3a4b69;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    min-height: 32px;
    border-radius: 999px;
    padding: 0.2rem 1.35rem;
    background: #cdeedf;
  }

  h1 {
    margin-top: 0.7rem;
    max-width: 15ch;
    font-size: clamp(3.2rem, 8.7vw, 7.6rem);
    line-height: 0.92;
    letter-spacing: -0.052em;
  }

  &__lede {
    margin: 1.16rem 0 0;
    max-width: 53ch;
    color: var(--text-2);
    font-size: clamp(1.06rem, 1.9vw, 1.28rem);
    line-height: 1.58;
  }

  &__try {
    margin-top: 1rem;
    min-height: 50px;
    padding-inline: 1.22rem;
  }

  &__mascot {
    width: clamp(156px, 19vw, 214px);
    aspect-ratio: 420 / 301;
    object-fit: cover;
    object-position: center;
    border-radius: 18px;
    box-shadow: var(--shadow-md);
  }

  &__demo {
    margin-top: 1.6rem;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 48%);
    border-radius: var(--radius-xl);
    background:
      radial-gradient(120% 140% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 24%), transparent 58%),
      radial-gradient(120% 120% at 0% 100%, color-mix(in srgb, var(--accent-soft), transparent 82%), transparent 60%),
      var(--surface-0);
    box-shadow: var(--shadow-lg);
    padding: clamp(1.2rem, 2.8vw, 1.8rem);
  }

  &__demo-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.12rem;
  }

  &__demo-title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-1);
  }

  &__demo-subtitle {
    margin: 0.24rem 0 0;
    color: var(--text-3);
    font-size: 0.9rem;
  }

  &__demo-actions {
    display: inline-flex;
    align-items: center;
    gap: 0.54rem;

    .btn {
      min-height: 42px;
      padding-inline: 0.94rem;
    }
  }

  &__demo-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 1.24rem;
  }

  &__panel {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 60%);
    border-radius: 16px;
    background:
      linear-gradient(160deg, color-mix(in srgb, var(--surface-1), white 28%), color-mix(in srgb, var(--surface-0), white 6%));
    min-height: 418px;
    padding: 1.04rem;
    box-shadow:
      inset 0 1px 0 color-mix(in srgb, white, transparent 34%),
      var(--shadow-sm);
  }

  &__panel--output {
    background:
      radial-gradient(130% 130% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 42%), transparent 58%),
      linear-gradient(180deg, color-mix(in srgb, var(--surface-0), var(--accent-soft) 22%), color-mix(in srgb, var(--surface-1), white 20%));
    transition: box-shadow 300ms ease, border-color 300ms ease;
  }

  &__panel--pulse {
    border-color: color-mix(in srgb, var(--accent-2), transparent 22%);
    box-shadow:
      0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 70%),
      var(--shadow-md);
  }

  &__panel-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.6rem;
  }

  &__label {
    margin: 0;
    color: var(--text-1);
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
  }

  &__chip {
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 32%);
    border-radius: 999px;
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 18%);
    color: var(--text-2);
    min-height: 36px;
    padding: 0.3rem 0.62rem;
    font-size: 0.76rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.34rem;
    cursor: pointer;
    transition: border-color 180ms ease, color 180ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      border-color: var(--border-strong);
      color: var(--text-1);
      box-shadow: var(--shadow-xs);
    }

    &:disabled {
      opacity: 0.46;
      cursor: not-allowed;
      box-shadow: none;
    }
  }

  &__textarea {
    margin-top: 0.72rem;
    width: 100%;
    min-height: 210px;
    max-height: 500px;
    resize: none;
    border-radius: var(--radius-md);
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 32%);
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 6%);
    color: var(--text-1);
    padding: 0.96rem 1rem;
    font-size: 0.98rem;
    line-height: 1.7;
    overflow: auto;
    transition: border-color 180ms ease, box-shadow 180ms ease;

    &::placeholder {
      color: color-mix(in srgb, var(--text-3), transparent 8%);
    }

    &:focus-visible {
      outline: none;
      border-color: color-mix(in srgb, var(--accent-2), transparent 18%);
      box-shadow: var(--ring);
    }
  }

  &__row {
    margin-top: 0.86rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.78rem;
  }

  &__live-detect {
    position: relative;
    display: grid;
    padding-left: 0.82rem;
    gap: 0.15rem;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0.34rem;
      width: 0.42rem;
      height: 0.42rem;
      border-radius: 999px;
      background: var(--accent-2);
      box-shadow: 0 0 0 5px color-mix(in srgb, var(--accent-2), transparent 86%);
    }

    strong {
      color: var(--text-1);
      font-size: 0.85rem;
      font-weight: 700;
    }

    span {
      color: var(--text-3);
      font-size: 0.79rem;
    }
  }

  &__sanitise {
    min-width: 190px;
    min-height: 48px;
  }

  &__options {
    margin-top: 0.74rem;
    display: grid;
    gap: 0.66rem;
  }

  &__mode {
    width: fit-content;
    max-width: 100%;
    display: inline-grid;
    grid-template-columns: auto auto;
    gap: 0.28rem;
    padding: 0.22rem;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-2), transparent 24%);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 10px;
    background: transparent;
    color: var(--text-3);
    font-size: 0.81rem;
    font-weight: 600;
    padding: 0.44rem 0.72rem;
    cursor: pointer;
    transition: color 180ms ease, background 180ms ease, border-color 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--surface-0), transparent 10%);
    }
  }

  &__mode-btn--active {
    color: var(--text-1);
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 24%);
    border-color: color-mix(in srgb, var(--border-2), transparent 24%);
    box-shadow: var(--shadow-xs);
  }

  &__transform-toggle {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 14%);
    color: var(--text-2);
    padding: 0.5rem 0.64rem;
    display: flex;
    align-items: center;
    gap: 0.48rem;
    text-align: left;
    cursor: pointer;
    transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;

    &:hover,
    &:focus-visible {
      border-color: var(--border-strong);
      box-shadow: var(--shadow-xs);
    }
  }

  &__transform-toggle--active {
    border-color: color-mix(in srgb, var(--accent-2), transparent 34%);
    background: color-mix(in srgb, var(--accent-soft), white 42%);
    color: var(--text-1);
  }

  &__transform-icon {
    width: 28px;
    height: 28px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--accent-1), white 82%);
    color: var(--accent-1);
    flex-shrink: 0;
  }

  &__transform-copy {
    display: grid;
    gap: 0.02rem;
    min-width: 0;
  }

  &__transform-label {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-1);
    line-height: 1.2;
  }

  &__transform-hint {
    font-size: 0.72rem;
    color: var(--text-3);
    line-height: 1.2;
  }

  &__transform-state {
    margin-left: auto;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 12%);
    background: color-mix(in srgb, var(--surface-2), transparent 8%);
    color: var(--text-2);
    padding: 0.18rem 0.5rem;
    font-size: 0.72rem;
    font-weight: 700;
    line-height: 1;
    flex-shrink: 0;
  }

  &__tag-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.46rem;
  }

  &__tag-chip {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 32%);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), white 8%);
    color: var(--text-2);
    padding: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.44rem;
    text-align: left;
    cursor: pointer;
    transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      border-color: var(--border-strong);
      box-shadow: var(--shadow-xs);
    }
  }

  &__tag-chip--active {
    border-color: color-mix(in srgb, var(--accent-2), transparent 36%);
    background: color-mix(in srgb, var(--accent-soft), white 42%);
    color: var(--text-1);
  }

  &__tag-icon {
    font-size: 0.94rem;
    line-height: 1;
  }

  &__tag-copy {
    display: grid;
    min-width: 0;
  }

  &__tag-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text-1);
  }

  &__tag-hint {
    font-size: 0.7rem;
    color: var(--text-3);
  }

  &__status {
    margin: 0.34rem 0 0;
    color: var(--accent-3);
    font-size: 0.83rem;
    font-weight: 600;
  }

  &__output-meta {
    margin: 0.56rem 0 0;
    color: var(--text-3);
    font-size: 0.8rem;
  }

  &__output-wrap {
    margin-top: 0.52rem;
    position: relative;
  }

  &__output {
    border: 0;
    border-radius: var(--radius-md);
    background:
      linear-gradient(
        180deg,
        color-mix(in srgb, var(--surface-0), white 5%),
        color-mix(in srgb, var(--surface-0), var(--accent-soft) 10%)
      );
    min-height: 318px;
    max-height: 500px;
    overflow: auto;
    padding: 1.08rem;
    font-size: 0.99rem;
    line-height: 1.74;
    color: var(--text-1);
    transition: background 240ms ease;
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--border-1), transparent 24%);
  }

  &__output--reveal {
    animation: output-reveal 320ms cubic-bezier(0.2, 0.9, 0.25, 1) both;
  }

  &__output-line {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }

  &__placeholder {
    margin: 0;
    color: var(--text-3);
    font-size: 0.93rem;
  }

  &__token {
    --token-bg: color-mix(in srgb, var(--accent-soft), white 50%);
    --token-border: color-mix(in srgb, var(--accent-2), transparent 44%);
    --token-text: color-mix(in srgb, var(--accent-3), black 12%);

    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    white-space: nowrap;
    border: 1px solid var(--token-border);
    background: var(--token-bg);
    color: var(--token-text);
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.87rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    padding: 0.18rem 0.62rem;
    margin: 0.04rem 0.16rem;
    box-shadow:
      inset 0 1px 0 color-mix(in srgb, white, transparent 42%),
      0 1px 3px color-mix(in srgb, var(--accent-2), transparent 86%);
    animation: token-reveal 280ms ease, token-flash 380ms ease;
  }

  &__token--person {
    --token-bg: color-mix(in srgb, #dbeafe, white 28%);
    --token-border: color-mix(in srgb, #3b82f6, transparent 48%);
    --token-text: color-mix(in srgb, #1d4ed8, #0f172a 26%);
  }

  &__token--organisation {
    --token-bg: color-mix(in srgb, #e9d5ff, white 30%);
    --token-border: color-mix(in srgb, #8b5cf6, transparent 46%);
    --token-text: color-mix(in srgb, #6d28d9, #0f172a 26%);
  }

  &__token--email {
    --token-bg: color-mix(in srgb, #dbeafe, white 34%);
    --token-border: color-mix(in srgb, #2563eb, transparent 46%);
    --token-text: color-mix(in srgb, #1e40af, #0f172a 24%);
  }

  &__token--phone {
    --token-bg: color-mix(in srgb, #cffafe, white 34%);
    --token-border: color-mix(in srgb, #0891b2, transparent 46%);
    --token-text: color-mix(in srgb, #155e75, #0f172a 24%);
  }

  &__token--address {
    --token-bg: color-mix(in srgb, #dcfce7, white 36%);
    --token-border: color-mix(in srgb, #16a34a, transparent 48%);
    --token-text: color-mix(in srgb, #166534, #0f172a 24%);
  }

  &__token--apikey,
  &__token--ipaddress {
    --token-bg: color-mix(in srgb, #fee2e2, white 34%);
    --token-border: color-mix(in srgb, #dc2626, transparent 52%);
    --token-text: color-mix(in srgb, #991b1b, #0f172a 20%);
  }

  &__spinner {
    position: absolute;
    right: 0.8rem;
    bottom: 0.8rem;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 44%);
    border-radius: 999px;
    padding: 0.3rem 0.58rem;
    background: color-mix(in srgb, var(--surface-0), white 8%);
    color: var(--accent-3);
    font-size: 0.76rem;
    font-weight: 700;
    box-shadow: var(--shadow-xs);
  }

  &__spinner-ring {
    width: 12px;
    height: 12px;
    border-radius: 999px;
    border: 2px solid color-mix(in srgb, var(--accent-2), transparent 78%);
    border-top-color: var(--accent-2);
    animation: hero-spin 680ms linear infinite;
  }
}

@keyframes hero-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes token-flash {
  from {
    filter: brightness(1.15);
  }
  to {
    filter: brightness(1);
  }
}

@keyframes token-reveal {
  from {
    opacity: 0;
    transform: translateY(3px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes output-reveal {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 980px) {
  .hero {
    &__header {
      grid-template-columns: 1fr;
      gap: 0.78rem;
    }

    &__mascot {
      width: 144px;
      justify-self: start;
    }

    &__demo-head {
      flex-direction: column;
      align-items: flex-start;
    }

    &__demo-grid {
      grid-template-columns: 1fr;
    }

    &__panel {
      min-height: 0;
    }

    &__tag-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
}

@media (max-width: 680px) {
  .hero {
    h1 {
      max-width: none;
      font-size: clamp(1.9rem, 9vw, 2.4rem);
    }

    &__demo {
      border-radius: 18px;
      padding: 0.82rem;
    }

    &__panel {
      border-radius: 14px;
      padding: 0.72rem;
    }

    &__demo-actions {
      width: 100%;

      .btn {
        flex: 1;
      }
    }

    &__row--cta {
      flex-direction: column;
      align-items: stretch;
    }

    &__mode {
      width: 100%;
      grid-template-columns: 1fr 1fr;
    }

    &__mode-btn {
      text-align: center;
      padding-inline: 0.4rem;
    }

    &__transform-toggle {
      width: 100%;
    }

    &__tag-grid {
      grid-template-columns: 1fr;
    }

    &__output {
      min-height: 248px;
      padding: 0.78rem;
      font-size: 0.92rem;
      line-height: 1.62;
    }

    &__token {
      font-size: 0.79rem;
      margin: 0.02rem 0.12rem;
    }
  }
}
</style>
