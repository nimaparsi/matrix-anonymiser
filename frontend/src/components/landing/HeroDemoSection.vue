<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

type TokenType = 'Person' | 'Organisation' | 'Email' | 'Phone' | 'Address' | 'ApiKey' | 'IpAddress'
type TagOption = {
  key: TokenType
  label: string
  hint: string
  icon: string
}

const inputText = ref('')
const outputText = ref('')
const copyLabel = ref('Copy output')
const statusMessage = ref('')
const isSanitising = ref(false)
const detectionMode = ref<'automatic' | 'custom'>('automatic')
const selectedTagKeys = ref<TokenType[]>(['Person', 'Organisation', 'Email', 'Phone', 'Address'])
const exampleButtonLabel = ref('Try example')
const inputEl = ref<HTMLTextAreaElement | null>(null)
let statusTimer: ReturnType<typeof window.setTimeout> | null = null
let sanitiseTimer: ReturnType<typeof window.setTimeout> | null = null
let exampleLabelTimer: ReturnType<typeof window.setTimeout> | null = null
const MIN_TEXTAREA_HEIGHT = 176
const TEXTAREA_VIEWPORT_OFFSET = 360
const TEXTAREA_MAX_HARD_CAP = 640
const SANITISE_SPINNER_MS = 420
const EXAMPLE_LABEL_RESET_MS = 10_000
const EXAMPLE_LABELS = ['Another one?', 'One more?', 'Keep going?'] as const
let exampleLabelIndex = 0
let lastGeneralExampleIndex = -1

const tagOptions: TagOption[] = [
  { key: 'Person', label: 'People', hint: 'Names', icon: '👤' },
  { key: 'Organisation', label: 'Organisation', hint: 'Company names', icon: '🏢' },
  { key: 'Email', label: 'Email', hint: 'Mail addresses', icon: '📧' },
  { key: 'Phone', label: 'Phone', hint: 'Phone numbers', icon: '📞' },
  { key: 'Address', label: 'Address', hint: 'Street/location', icon: '📍' },
  { key: 'ApiKey', label: 'API keys', hint: 'Tokens and keys', icon: '🔐' },
  { key: 'IpAddress', label: 'IP address', hint: 'IPv4 hosts', icon: '🌐' },
]

const defaultExampleText = [
  'John Smith from Acme emailed john@acme.com about Thursday delivery.',
  'GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN6q9kZr7mP2xT4vB8dQ1wE5rY3uN7hL2cF9pJ6x dev@acme-laptop',
  'Call me on 07912 345678 if anything changes.',
].join('\n')

const generalExamples = [
  defaultExampleText,
  [
    'Support escalation email',
    'From: Daniel Hughes at Northbridge Payments',
    'Issue: customer refund failed on invoice batch 4913.',
    'Contact: daniel.hughes@northbridgepay.co.uk',
    'Phone: +44 7700 901245',
    'Follow-up address: 22 Cedar Road, Leeds',
    'Access token: access_token=prod_7cN92aLm4Qx8rJ1vT6wE5yU2',
  ].join('\n'),
  [
    'Recruiter interview summary',
    'Candidate: Sofia Martinez',
    'Current company: Urban Growth Initiative',
    'Email: sofia.martinez@urbangrowth.co.uk',
    'Mobile: 07700 903876',
    'Address provided for payroll checks: 55 Orchard Street, Manchester',
  ].join('\n'),
  [
    'Consulting workshop notes',
    'Prepared by: Anna Carter from Green Horizon Research',
    'Client contact: Ravi Patel at Future Energy Alliance',
    'Emails: anna.carter@example.com, ravi.patel@futureenergy.org',
    'Dial-in backup: +44 7700 905112',
    'Meeting venue: 14 Willow Lane, Brighton',
    'API key used in dashboard: api_key=live_5dQ8mT2xN7kV4rY1pL6sF9cB',
  ].join('\n'),
  [
    'Contract clause draft',
    'This agreement is between Emily Foster and Coastal Lab.',
    'Notices should be sent to emily.foster@coastallab.net.',
    'Registered office: 3 Harbour View Road, Southampton.',
    'Urgent legal contact: +44 7700 907331.',
  ].join('\n'),
  [
    'Student request to tutor',
    'Hi, I am Liam Turner and I need feedback before submission.',
    'University email: liam.turner@studentmail.ac.uk',
    'My number is 07888 102233 and I am currently staying at 8 Pine Close, Bristol.',
    'I am working with Dr Sarah Khan on the final report.',
  ].join('\n'),
  [
    'Operations incident report',
    'Reported by: Priya Shah at FinCore Ltd',
    'Pager: +44 7700 990112',
    'Email: priya.shah@fincore.co.uk',
    'Source host observed in logs: 10.24.8.19',
    'Dispatch team location: 41 Mill Avenue, London',
    'Bearer token seen in trace: bearer_tk_f4Kp8sM2xJ7vN1qL6dR9wE3',
  ].join('\n'),
  [
    'Immigration document prep note',
    'Applicant: Kamran Ali',
    'Sponsor organisation: BrightEdge Consulting',
    'Primary contact: kamran.ali@brightedge.co.uk',
    'Phone: 07933 449922',
    'Correspondence address: 19 Riverside Drive, Birmingham',
  ].join('\n'),
]

const useCaseExamples: Record<string, string> = {
  Developers: [
    'GitHub production incident ticket',
    'Reporter: Alice Morgan',
    'Email: alice.morgan@contoso.dev',
    'Phone: +44 7700 900456',
    'Host: 10.12.8.32',
    'GitHub SSH key on file: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFl2dD9pQm7rX4uN8wE1yT5kL3cB6vR2pH0sJ9n alice@contoso-dev',
    'Service API key: api_key=prod_9fH3mQ7xV2pL5rT8kN1dW4cY',
    'Webhook secret: access_token=svc_7aL2nP9xR4mK6vT1qD8eY5',
    'Issue reproduced on invoice-service in London office.',
  ].join('\n'),
  Recruiters: [
    'Candidate profile summary',
    'Name: Daniel Hughes',
    'Email: daniel.hughes@careersmail.com',
    'Phone: 07912 123456',
    'Address: 21 Cedar Avenue, Manchester',
    'Current employer: Green Horizon Research',
    'Reference contact: Priya Shah, priya.shah@referencehub.co.uk',
  ].join('\n'),
  Consultants: [
    'Client workshop prep memo',
    'Prepared for: Sofia Martinez',
    'Contact: sofia.martinez@clientgroup.co.uk',
    'Mobile: +44 7700 903876',
    'Office: 14 Willow Lane, Brighton',
    'Organisation: Urban Growth Initiative',
    'Client endpoint: 192.168.20.45',
  ].join('\n'),
  Students: [
    'Coursework submission context',
    'Student: Ravi Patel',
    'University email: ravi.patel@studentmail.ac.uk',
    'Phone: 07700 905112',
    'Placement company: Future Energy Alliance',
    'Reference address: 55 Orchard Street, Manchester',
    'Supervisor: Emily Foster (emily.foster@coastallab.net)',
  ].join('\n'),
}

type TryExampleEvent = CustomEvent<{
  useCase?: string
  quickStart?: boolean
  text?: string
  instant?: boolean
  focus?: boolean
}>

const hasInput = computed(() => inputText.value.trim().length > 0)
const hasOutput = computed(() => outputText.value.trim().length > 0)
const enabledTagSet = computed(() =>
  detectionMode.value === 'automatic'
    ? new Set<TokenType>(tagOptions.map((tag) => tag.key))
    : new Set<TokenType>(selectedTagKeys.value),
)
const activeCustomTagCount = computed(() => selectedTagKeys.value.length)
const modeSummary = computed(() =>
  detectionMode.value === 'automatic'
    ? 'All detectors active'
    : `${activeCustomTagCount.value} custom detectors active`,
)
const activeTagPreview = computed(() => {
  const keys =
    detectionMode.value === 'automatic'
      ? tagOptions.map((tag) => tag.key)
      : selectedTagKeys.value
  return tagOptions
    .filter((tag) => keys.includes(tag.key))
    .slice(0, 4)
    .map((tag) => tag.label)
    .join(' · ')
})

function setStatus(message: string, timeout = 2200) {
  statusMessage.value = message
  if (statusTimer) window.clearTimeout(statusTimer)
  statusTimer = window.setTimeout(() => {
    statusMessage.value = ''
    statusTimer = null
  }, timeout)
}

function normaliseKey(value: string) {
  return value.trim().toLowerCase()
}

function anonymise(rawText: string, enabledTags: Set<TokenType>) {
  if (!rawText.trim()) return ''

  const tokenMaps: Record<TokenType, Map<string, string>> = {
    Person: new Map<string, string>(),
    Organisation: new Map<string, string>(),
    Email: new Map<string, string>(),
    Phone: new Map<string, string>(),
    Address: new Map<string, string>(),
    ApiKey: new Map<string, string>(),
    IpAddress: new Map<string, string>(),
  }

  const tokenCounts: Record<TokenType, number> = {
    Person: 0,
    Organisation: 0,
    Email: 0,
    Phone: 0,
    Address: 0,
    ApiKey: 0,
    IpAddress: 0,
  }

  const tokenFor = (type: TokenType, value: string) => {
    const key = normaliseKey(value)
    const existing = tokenMaps[type].get(key)
    if (existing) return existing
    tokenCounts[type] += 1
    const token = `[${type} ${tokenCounts[type]}]`
    tokenMaps[type].set(key, token)
    return token
  }

  let transformed = rawText

  const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g
  const phoneRegex = /\b(?:\+?\d[\d\s().-]{7,}\d)\b/g
  const addressRegex = /\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\s(?:Street|Road|Lane|Avenue|Drive|Court|Close|Way)\b/g
  const ipRegex = /\b(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}\b/g
  const apiKeyRegex =
    /\b(?:ssh-(?:rsa|ed25519)\s+[A-Za-z0-9+/=]{40,}|(?:api[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*[A-Za-z0-9._\-]{16,}|bearer[_-]?[a-z0-9._\-]{16,}|token_[A-Za-z0-9._\-]{16,})\b/gi

  if (enabledTags.has('ApiKey')) {
    transformed = transformed.replace(apiKeyRegex, (match) => tokenFor('ApiKey', match))
  }
  if (enabledTags.has('IpAddress')) {
    transformed = transformed.replace(ipRegex, (match) => tokenFor('IpAddress', match))
  }
  if (enabledTags.has('Email')) {
    transformed = transformed.replace(emailRegex, (match) => tokenFor('Email', match))
  }
  if (enabledTags.has('Phone')) {
    transformed = transformed.replace(phoneRegex, (match) => tokenFor('Phone', match))
  }
  if (enabledTags.has('Address')) {
    transformed = transformed.replace(addressRegex, (match) => tokenFor('Address', match))
  }

  if (enabledTags.has('Organisation')) {
    transformed = transformed.replace(/\b(from|at|with)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\b/g, (full, connector: string, name: string) => {
      if (name.startsWith('[')) return full
      if (/^[A-Z][a-z]+\s+[A-Z][a-z]+$/.test(name)) return full
      return `${connector} ${tokenFor('Organisation', name)}`
    })
  }

  if (enabledTags.has('Person')) {
    transformed = transformed.replace(/\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b/g, (match) => {
      if (match.startsWith('[')) return match
      return tokenFor('Person', match)
    })
  }

  return transformed
}

async function sanitiseNow() {
  if (!hasInput.value || isSanitising.value) return
  isSanitising.value = true
  outputText.value = ''

  await new Promise<void>((resolve) => {
    sanitiseTimer = window.setTimeout(() => {
      sanitiseTimer = null
      resolve()
    }, SANITISE_SPINNER_MS)
  })

  outputText.value = anonymise(inputText.value, enabledTagSet.value)
  copyLabel.value = 'Copy output'
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

function applyCustomPreset(preset: 'contact' | 'infra' | 'all') {
  if (preset === 'contact') {
    selectedTagKeys.value = ['Person', 'Organisation', 'Email', 'Phone', 'Address']
    setStatus('Contact preset loaded')
    return
  }
  if (preset === 'infra') {
    selectedTagKeys.value = ['ApiKey', 'IpAddress', 'Email']
    setStatus('Infra preset loaded')
    return
  }
  selectedTagKeys.value = tagOptions.map((tag) => tag.key)
  setStatus('All custom rules enabled')
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
  return Math.max(
    MIN_TEXTAREA_HEIGHT,
    Math.min(TEXTAREA_MAX_HARD_CAP, viewportHeight - TEXTAREA_VIEWPORT_OFFSET),
  )
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

  if (generalExamples.length < 2) return generalExamples[0]

  let nextIndex = Math.floor(Math.random() * generalExamples.length)
  if (nextIndex === lastGeneralExampleIndex) {
    nextIndex = (nextIndex + 1) % generalExamples.length
  }
  lastGeneralExampleIndex = nextIndex
  return generalExamples[nextIndex]
}

function advanceExampleButtonLabel() {
  exampleButtonLabel.value = EXAMPLE_LABELS[exampleLabelIndex]
  exampleLabelIndex = (exampleLabelIndex + 1) % EXAMPLE_LABELS.length

  if (exampleLabelTimer) window.clearTimeout(exampleLabelTimer)
  exampleLabelTimer = window.setTimeout(() => {
    exampleButtonLabel.value = 'Try example'
    exampleLabelTimer = null
  }, EXAMPLE_LABEL_RESET_MS)
}

async function applyExample(useCase?: string) {
  inputText.value = pickExampleText(useCase)
  await sanitiseNow()
  advanceExampleButtonLabel()
  setStatus('Example loaded')
}

function clearDemo() {
  cancelSanitiseTimer()
  isSanitising.value = false
  inputText.value = ''
  outputText.value = ''
  copyLabel.value = 'Copy output'
  statusMessage.value = ''
  if (exampleLabelTimer) {
    window.clearTimeout(exampleLabelTimer)
    exampleLabelTimer = null
  }
  exampleButtonLabel.value = 'Try example'
}

async function pasteFromClipboard() {
  try {
    const clipboardText = await navigator.clipboard.readText()
    if (!clipboardText.trim()) {
      setStatus('Clipboard is empty')
      return
    }
    inputText.value = clipboardText
    setStatus('Pasted from clipboard')
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

    if (detail.instant ?? true) {
      outputText.value = anonymise(inputText.value, enabledTagSet.value)
      copyLabel.value = 'Copy output'
      setStatus('Example ready')
    } else {
      void sanitiseNow()
    }

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
  if (exampleLabelTimer) {
    window.clearTimeout(exampleLabelTimer)
    exampleLabelTimer = null
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
    <div class="hero__shell">
      <div class="hero__head">
        <div class="hero__copy">
          <p class="hero__eyebrow">Private by design</p>
          <h1 id="hero-title">Sanitise sensitive text before sending it to AI</h1>
          <p class="hero__lede">
            Create clean, safe-to-share prompts in seconds. Detect sensitive details and replace them with structured
            placeholders while preserving meaning.
          </p>
          <div class="hero__proof" aria-label="Key product benefits">
            <span class="hero__proof-item">No signup required</span>
            <span class="hero__proof-item">Instant sanitisation</span>
            <span class="hero__proof-item">Token-safe output</span>
          </div>
        </div>

        <aside class="hero__stat-card" aria-label="Demo quick facts">
          <img
            class="hero__stat-mascot"
            src="/sanitise-ai-logo-trimmed.png"
            alt=""
            aria-hidden="true"
          />
          <p class="hero__stat-title">Detection console</p>
          <ul>
            <li><span>Mode</span><strong>{{ modeSummary }}</strong></li>
            <li><span>Current tags</span><strong>{{ activeTagPreview || 'None' }}</strong></li>
            <li><span>Run action</span><strong>Cmd/Ctrl + Enter</strong></li>
            <li><span>Data storage</span><strong>None in demo mode</strong></li>
          </ul>
        </aside>
      </div>

      <article class="hero__demo" aria-label="Interactive anonymisation demo">
        <div class="hero__demo-grid">
          <section class="hero__panel">
            <div class="hero__panel-top">
              <label class="hero__label" for="demo-input">Paste your text</label>
              <button class="hero__chip" type="button" @click="pasteFromClipboard">Paste clipboard</button>
            </div>
            <textarea
              id="demo-input"
              ref="inputEl"
              v-model="inputText"
              class="hero__textarea"
              placeholder="Paste text containing sensitive details..."
              @keydown="handleInputKeydown"
            ></textarea>
            <div class="hero__actions">
              <button class="hero__btn hero__btn--primary" type="button" :disabled="!hasInput || isSanitising" @click="sanitiseNow">Sanitise text</button>
              <button class="hero__btn hero__btn--secondary" type="button" :disabled="isSanitising" @click="applyExample">{{ exampleButtonLabel }}</button>
              <button class="hero__btn hero__btn--ghost" type="button" :disabled="!hasInput || isSanitising" @click="clearDemo">Clear</button>
            </div>
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
            <div v-if="detectionMode === 'custom'" class="hero__custom-rules" aria-live="polite">
              <div class="hero__custom-head">
                <p class="hero__custom-title">Custom detection rules</p>
                <span class="hero__custom-count">{{ activeCustomTagCount }} selected</span>
              </div>
              <div class="hero__custom-presets">
                <button type="button" class="hero__preset-btn" @click="applyCustomPreset('contact')">Contact preset</button>
                <button type="button" class="hero__preset-btn" @click="applyCustomPreset('infra')">Infra preset</button>
                <button type="button" class="hero__preset-btn" @click="applyCustomPreset('all')">Select all</button>
              </div>
              <div class="hero__tag-grid">
                <button
                  v-for="tag in tagOptions"
                  :key="tag.key"
                  type="button"
                  class="hero__tag-chip"
                  :class="{ 'hero__tag-chip--active': isTagEnabled(tag.key) }"
                  @click="toggleTag(tag.key)"
                >
                  <span class="hero__tag-icon" aria-hidden="true">{{ tag.icon }}</span>
                  <span class="hero__tag-text">
                    <span class="hero__tag-label">{{ tag.label }}</span>
                    <span class="hero__tag-hint">{{ tag.hint }}</span>
                  </span>
                </button>
              </div>
            </div>
            <p v-if="statusMessage" class="hero__status" role="status" aria-live="polite">{{ statusMessage }}</p>
          </section>

          <section class="hero__panel hero__panel--output">
            <div class="hero__panel-top">
              <p class="hero__label">Sanitised output</p>
              <button class="hero__chip" type="button" :disabled="!hasOutput || isSanitising" @click="copyOutput">{{ copyLabel }}</button>
            </div>
            <p class="hero__output-meta">{{ modeSummary }} <span v-if="activeTagPreview">· {{ activeTagPreview }}</span></p>
            <div class="hero__output-wrap">
              <pre class="hero__output">{{ outputText || 'Sanitised output appears here.' }}</pre>
              <div v-if="isSanitising" class="hero__spinner" role="status" aria-live="polite">
                <span class="hero__spinner-ring" aria-hidden="true"></span>
                <span>Sanitising...</span>
              </div>
            </div>
          </section>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.hero {
  &__shell {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border-1);
    border-radius: 34px;
    background:
      radial-gradient(760px 280px at -6% -10%, color-mix(in srgb, var(--accent-2), transparent 82%) 0%, transparent 66%),
      radial-gradient(520px 240px at 96% 2%, color-mix(in srgb, var(--accent-1), transparent 84%) 0%, transparent 68%),
      color-mix(in srgb, var(--surface-glass), transparent 2%);
    box-shadow: var(--shadow-lg);
    padding: clamp(1rem, 2.4vw, 1.45rem);
    backdrop-filter: blur(16px) saturate(125%);

    &::after {
      content: '';
      position: absolute;
      inset: 0;
      pointer-events: none;
      border-radius: inherit;
      box-shadow:
        inset 0 1px 0 color-mix(in srgb, var(--accent-2), transparent 86%),
        inset 0 -1px 0 color-mix(in srgb, var(--accent-1), transparent 92%);
    }
  }

  &__head {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(290px, 340px);
    gap: 1rem;
    align-items: start;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 700;
  }

  h1 {
    margin: 0.46rem 0 0;
    color: var(--text-1);
    font-size: clamp(1.95rem, 5vw, 3.15rem);
    line-height: 1.02;
    letter-spacing: -0.032em;
    max-width: 18ch;
    text-wrap: balance;
  }

  &__lede {
    margin: 0.82rem 0 0;
    color: var(--text-2);
    font-size: 1rem;
    line-height: 1.62;
    max-width: 62ch;
  }

  &__proof {
    margin-top: 0.82rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.38rem;
  }

  &__proof-item {
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 66%);
    border-radius: 999px;
    padding: 0.24rem 0.56rem;
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--text-2);
    background: color-mix(in srgb, var(--surface-0), transparent 2%);
    box-shadow: var(--shadow-xs);
  }

  &__stat-card {
    border: 1px solid var(--border-1);
    border-radius: 18px;
    background:
      linear-gradient(
        154deg,
        color-mix(in srgb, var(--surface-1), var(--accent-2) 9%),
        color-mix(in srgb, var(--surface-0), transparent 0%)
      );
    padding: 0.8rem;
    box-shadow: var(--shadow-sm);
    position: relative;

    ul {
      list-style: none;
      margin: 0.54rem 0 0;
      padding: 0;
      display: grid;
      gap: 0.48rem;
    }

    li {
      display: flex;
      justify-content: space-between;
      gap: 0.7rem;
      font-size: 0.8rem;
      color: var(--text-2);

      span {
        opacity: 0.95;
      }

      strong {
        color: var(--text-1);
        font-size: 0.8rem;
        max-width: 64%;
        text-align: right;
      }
    }
  }

  &__stat-title {
    margin: 0;
    color: var(--text-1);
    font-size: 0.88rem;
    font-weight: 700;
  }

  &__stat-mascot {
    width: 118px;
    aspect-ratio: 420 / 301;
    object-fit: cover;
    object-position: center;
    display: block;
    margin: -0.22rem -0.22rem 0.4rem auto;
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 74%);
    background: color-mix(in srgb, var(--surface-0), transparent 0%);
    box-shadow: var(--shadow-xs);
  }

  &__demo {
    margin-top: 1rem;
    border: 1px solid var(--border-1);
    border-radius: 22px;
    background:
      linear-gradient(
        180deg,
        color-mix(in srgb, var(--surface-1), white 4%),
        color-mix(in srgb, var(--surface-0), transparent 2%)
      );
    padding: 0.9rem;
    box-shadow: var(--shadow-sm);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      left: 16px;
      right: 16px;
      top: 0;
      height: 1px;
      background: linear-gradient(
        90deg,
        transparent,
        color-mix(in srgb, var(--accent-2), transparent 45%),
        color-mix(in srgb, var(--accent-1), transparent 45%),
        transparent
      );
      pointer-events: none;
    }
  }

  &__demo-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.86rem;
  }

  &__panel {
    border: 1px solid var(--border-1);
    border-radius: 16px;
    background: linear-gradient(180deg, color-mix(in srgb, var(--surface-0), white 7%), var(--surface-1));
    padding: 0.82rem;
    min-height: 288px;
    box-shadow: var(--shadow-xs);
  }

  &__panel--output {
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--surface-1), var(--accent-2) 4%),
      color-mix(in srgb, var(--surface-0), transparent 0%)
    );
  }

  &__panel-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.56rem;
  }

  &__label {
    margin: 0;
    color: var(--text-1);
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 0.01em;
  }

  &__chip {
    border: 1px solid var(--border-2);
    border-radius: 999px;
    background: linear-gradient(180deg, color-mix(in srgb, var(--surface-0), white 14%), var(--surface-1));
    color: var(--text-1);
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.34rem 0.64rem;
    cursor: pointer;
    box-shadow: var(--shadow-xs);
    transition: background 160ms ease, border-color 160ms ease, transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      background: color-mix(in srgb, var(--surface-2), var(--accent-2) 8%);
      border-color: color-mix(in srgb, var(--accent-2), transparent 48%);
      transform: translateY(-1px);
      box-shadow: var(--shadow-sm);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  &__textarea {
    margin-top: 0.62rem;
    width: 100%;
    min-height: 176px;
    resize: none;
    border-radius: 12px;
    border: 1px solid var(--border-2);
    background: color-mix(in srgb, var(--surface-0), white 10%);
    color: var(--text-1);
    padding: 0.74rem 0.82rem;
    line-height: 1.6;
    font-size: 0.95rem;
    max-height: 380px;
    overflow: auto;
    transition: border-color 180ms ease, box-shadow 180ms ease;

    &::placeholder {
      color: var(--text-3);
    }

    &:focus-visible {
      outline: none;
      border-color: color-mix(in srgb, var(--accent-2), transparent 34%);
      box-shadow:
        0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 36%),
        0 0 0 4px color-mix(in srgb, var(--accent-2), transparent 82%);
    }
  }

  &__actions {
    margin-top: 0.65rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  &__btn {
    border: 1px solid var(--border-2);
    border-radius: 12px;
    padding: 0.56rem 0.88rem;
    font-size: 0.86rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    cursor: pointer;
    transition: transform 160ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;

    &:disabled {
      opacity: 0.42;
      cursor: not-allowed;
      box-shadow: none;
      transform: none;
    }
  }

  &__btn--primary {
    color: var(--accent-ink);
    border-color: color-mix(in srgb, var(--accent-2), transparent 45%);
    background: linear-gradient(145deg, var(--accent-1), var(--accent-2));
    box-shadow:
      0 12px 26px color-mix(in srgb, var(--accent-2), transparent 66%),
      inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 88%);

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow:
        0 16px 32px color-mix(in srgb, var(--accent-2), transparent 58%),
        inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 86%);
    }
  }

  &__btn--secondary {
    color: var(--text-1);
    border-color: var(--border-2);
    background: linear-gradient(180deg, color-mix(in srgb, var(--surface-0), white 12%), var(--surface-1));
    box-shadow: var(--shadow-xs);

    &:hover,
    &:focus-visible {
      background: color-mix(in srgb, var(--surface-2), var(--accent-2) 8%);
      border-color: color-mix(in srgb, var(--accent-2), transparent 52%);
      transform: translateY(-1px);
      box-shadow: var(--shadow-sm);
    }
  }

  &__btn--ghost {
    color: var(--text-2);
    border-color: var(--border-1);
    background: color-mix(in srgb, var(--surface-1), transparent 4%);
    box-shadow: var(--shadow-xs);

    &:hover,
    &:focus-visible {
      background: color-mix(in srgb, var(--surface-2), transparent 4%);
      border-color: var(--border-2);
      transform: translateY(-1px);
    }
  }

  &__mode {
    margin-top: 0.58rem;
    display: inline-flex;
    gap: 0.36rem;
    padding: 0.24rem;
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-2), transparent 3%);
    border: 1px solid var(--border-1);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 10px;
    background: transparent;
    color: var(--text-2);
    font-size: 0.79rem;
    font-weight: 700;
    padding: 0.36rem 0.66rem;
    cursor: pointer;
    transition: background 160ms ease, color 160ms ease, border-color 160ms ease;
  }

  &__mode-btn--active {
    color: var(--text-1);
    background: color-mix(in srgb, var(--surface-0), white 8%);
    border-color: var(--border-2);
    box-shadow: var(--shadow-xs);
  }

  &__custom-rules {
    margin-top: 0.6rem;
    border: 1px solid var(--border-1);
    border-radius: 12px;
    padding: 0.58rem;
    background: color-mix(in srgb, var(--surface-1), transparent 3%);
    box-shadow: var(--shadow-xs);
  }

  &__custom-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.45rem;
  }

  &__custom-title {
    margin: 0;
    color: var(--text-1);
    font-size: 0.8rem;
    font-weight: 700;
  }

  &__custom-count {
    border: 1px solid var(--border-2);
    border-radius: 999px;
    padding: 0.14rem 0.46rem;
    color: var(--text-2);
    font-size: 0.74rem;
    font-weight: 700;
    background: color-mix(in srgb, var(--surface-0), transparent 4%);
  }

  &__custom-presets {
    margin-top: 0.46rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.38rem;
  }

  &__preset-btn {
    border: 1px solid var(--border-1);
    border-radius: 9px;
    padding: 0.26rem 0.52rem;
    background: color-mix(in srgb, var(--surface-0), transparent 4%);
    color: var(--text-2);
    font-size: 0.74rem;
    font-weight: 700;
    cursor: pointer;
    transition: border-color 160ms ease, background 160ms ease, color 160ms ease;

    &:hover,
    &:focus-visible {
      border-color: var(--border-2);
      background: color-mix(in srgb, var(--surface-2), var(--accent-2) 8%);
      color: var(--text-1);
    }
  }

  &__tag-grid {
    margin-top: 0.5rem;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.34rem;
  }

  &__tag-chip {
    border: 1px solid var(--border-1);
    border-radius: 10px;
    padding: 0.38rem;
    background: color-mix(in srgb, var(--surface-0), transparent 6%);
    color: var(--text-2);
    display: flex;
    align-items: center;
    gap: 0.4rem;
    cursor: pointer;
    text-align: left;
    transition: border-color 170ms ease, background 170ms ease, transform 170ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      border-color: var(--border-2);
      box-shadow: var(--shadow-xs);
    }
  }

  &__tag-chip--active {
    border-color: color-mix(in srgb, var(--accent-2), transparent 44%);
    background: linear-gradient(
      170deg,
      color-mix(in srgb, var(--surface-2), var(--accent-2) 12%),
      color-mix(in srgb, var(--surface-1), transparent 0%)
    );
    color: var(--text-1);
    box-shadow: var(--shadow-xs);
  }

  &__tag-icon {
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 9px;
    border: 1px solid var(--border-1);
    background: color-mix(in srgb, var(--surface-2), transparent 2%);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 0.82rem;
  }

  &__tag-text {
    display: grid;
    gap: 0.06rem;
    min-width: 0;
  }

  &__tag-label {
    font-size: 0.76rem;
    font-weight: 700;
    color: var(--text-1);
    line-height: 1.2;
  }

  &__tag-hint {
    font-size: 0.68rem;
    color: var(--text-3);
    line-height: 1.2;
  }

  &__status {
    margin: 0.56rem 0 0;
    color: var(--accent-2);
    font-size: 0.82rem;
    font-weight: 600;
  }

  &__output-meta {
    margin: 0.5rem 0 0;
    color: var(--text-3);
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.01em;
  }

  &__output-wrap {
    position: relative;
  }

  &__output {
    margin: 0.52rem 0 0;
    min-height: 220px;
    max-height: 380px;
    border-radius: 12px;
    border: 1px solid var(--border-1);
    background: color-mix(in srgb, var(--surface-0), transparent 0%);
    color: var(--text-1);
    font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace;
    font-size: 0.94rem;
    padding: 0.75rem 0.82rem;
    line-height: 1.56;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
    overflow: auto;
  }

  &__spinner {
    position: absolute;
    right: 0.72rem;
    bottom: 0.72rem;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border: 1px solid var(--border-2);
    border-radius: 999px;
    background: color-mix(in srgb, var(--surface-0), transparent 7%);
    color: var(--accent-2);
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.26rem 0.5rem;
    backdrop-filter: blur(2px);
  }

  &__spinner-ring {
    width: 13px;
    height: 13px;
    border-radius: 999px;
    border: 2px solid color-mix(in srgb, var(--accent-2), transparent 75%);
    border-top-color: var(--accent-2);
    animation: hero-spin 720ms linear infinite;
  }
}

@keyframes hero-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 980px) {
  .hero {
    &__head {
      grid-template-columns: 1fr;
    }

    h1 {
      max-width: none;
    }

    &__stat-card {
      max-width: 500px;
    }

    &__demo-grid {
      grid-template-columns: 1fr;
      gap: 0.72rem;
    }

    &__panel {
      min-height: 0;
    }
  }
}

@media (max-width: 680px) {
  .hero {
    &__shell {
      border-radius: 22px;
      padding: 0.84rem;
    }

    &__demo {
      margin-top: 0.84rem;
      border-radius: 14px;
      padding: 0.6rem;
    }

    &__panel {
      border-radius: 12px;
      padding: 0.62rem;
    }

    &__lede {
      font-size: 0.95rem;
      line-height: 1.54;
    }

    &__proof {
      gap: 0.3rem;
    }

    &__proof-item {
      font-size: 0.7rem;
      padding: 0.22rem 0.48rem;
    }

    &__stat-mascot {
      width: 96px;
    }

    &__btn {
      flex: 1 1 auto;
      min-width: 124px;
    }

    &__mode {
      width: 100%;
      display: grid;
      grid-template-columns: 1fr 1fr;
    }

    &__mode-btn {
      width: 100%;
      text-align: center;
    }

    &__tag-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
