<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

type TokenType = 'Person' | 'Organisation' | 'Email' | 'Phone' | 'Address' | 'ApiKey' | 'IpAddress'

const inputText = ref('')
const outputText = ref('')
const copyLabel = ref('Copy output')
const statusMessage = ref('')
const isSanitising = ref(false)
const detectionMode = ref<'automatic' | 'custom'>('automatic')
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

function anonymise(rawText: string) {
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

  transformed = transformed.replace(apiKeyRegex, (match) => tokenFor('ApiKey', match))
  transformed = transformed.replace(ipRegex, (match) => tokenFor('IpAddress', match))
  transformed = transformed.replace(emailRegex, (match) => tokenFor('Email', match))
  transformed = transformed.replace(phoneRegex, (match) => tokenFor('Phone', match))
  transformed = transformed.replace(addressRegex, (match) => tokenFor('Address', match))

  transformed = transformed.replace(/\b(from|at|with)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\b/g, (full, connector: string, name: string) => {
    if (name.startsWith('[')) return full
    if (/^[A-Z][a-z]+\s+[A-Z][a-z]+$/.test(name)) return full
    return `${connector} ${tokenFor('Organisation', name)}`
  })

  transformed = transformed.replace(/\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b/g, (match) => {
    if (match.startsWith('[')) return match
    return tokenFor('Person', match)
  })

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

  outputText.value = anonymise(inputText.value)
  copyLabel.value = 'Copy output'
  isSanitising.value = false
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
      outputText.value = anonymise(inputText.value)
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
        </div>

        <aside class="hero__stat-card" aria-label="Demo quick facts">
          <p class="hero__stat-title">Live demo</p>
          <ul>
            <li><span>Entity types</span><strong>Names, Email, Phone</strong></li>
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
            <p v-if="statusMessage" class="hero__status" role="status" aria-live="polite">{{ statusMessage }}</p>
          </section>

          <section class="hero__panel hero__panel--output">
            <div class="hero__panel-top">
              <p class="hero__label">Sanitised output</p>
              <button class="hero__chip" type="button" :disabled="!hasOutput || isSanitising" @click="copyOutput">{{ copyLabel }}</button>
            </div>
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
    border: 1px solid #dbe4f5;
    border-radius: 28px;
    background:
      radial-gradient(780px 220px at 0% 0%, rgba(59, 130, 246, 0.1) 0%, transparent 58%),
      #ffffff;
    box-shadow: 0 26px 54px rgba(15, 23, 42, 0.09);
    padding: clamp(1rem, 2.3vw, 1.55rem);
  }

  &__head {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(260px, 320px);
    gap: 1rem;
    align-items: start;
  }

  &__eyebrow {
    margin: 0;
    color: #1d4ed8;
    font-size: 0.82rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 700;
  }

  h1 {
    margin: 0.45rem 0 0;
    color: #0f172a;
    font-size: clamp(1.8rem, 4.8vw, 3rem);
    line-height: 1.06;
    letter-spacing: -0.03em;
    max-width: 20ch;
  }

  &__lede {
    margin: 0.82rem 0 0;
    color: #475569;
    font-size: 1rem;
    line-height: 1.58;
    max-width: 60ch;
  }

  &__stat-card {
    border: 1px solid #d6e2f7;
    border-radius: 18px;
    background: #f8fbff;
    padding: 0.8rem;

    ul {
      list-style: none;
      margin: 0.5rem 0 0;
      padding: 0;
      display: grid;
      gap: 0.46rem;
    }

    li {
      display: flex;
      justify-content: space-between;
      gap: 0.7rem;
      font-size: 0.82rem;
      color: #475569;

      strong {
        color: #0f172a;
        font-size: 0.82rem;
      }
    }
  }

  &__stat-title {
    margin: 0;
    color: #0f172a;
    font-size: 0.9rem;
    font-weight: 700;
  }

  &__demo {
    margin-top: 1.05rem;
    border: 1px solid #dce5f6;
    border-radius: 20px;
    background: #fbfdff;
    padding: 0.92rem;
  }

  &__demo-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
  }

  &__panel {
    border: 1px solid #d7e2f5;
    border-radius: 16px;
    background: #ffffff;
    padding: 0.85rem;
    min-height: 288px;
  }

  &__panel--output {
    background: #f8fbff;
  }

  &__panel-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.56rem;
  }

  &__label {
    margin: 0;
    color: #1e293b;
    font-size: 0.9rem;
    font-weight: 700;
  }

  &__chip {
    border: 1px solid #c8dbf7;
    border-radius: 999px;
    background: linear-gradient(180deg, #f8fbff, #ecf3ff);
    color: #1e40af;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.34rem 0.64rem;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.08);
    transition: background 160ms ease, border-color 160ms ease, transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      background: #dbeafe;
      border-color: #93c5fd;
      transform: translateY(-1px);
      box-shadow: 0 8px 18px rgba(37, 99, 235, 0.14);
    }

    &:disabled {
      opacity: 0.56;
      cursor: not-allowed;
    }
  }

  &__textarea {
    margin-top: 0.62rem;
    width: 100%;
    min-height: 176px;
    resize: none;
    border-radius: 12px;
    border: 1px solid #ccdbf2;
    background: #ffffff;
    color: #0f172a;
    padding: 0.75rem 0.82rem;
    line-height: 1.58;
    max-height: 380px;
    overflow: auto;
    transition: border-color 180ms ease, box-shadow 180ms ease;

    &::placeholder {
      color: #94a3b8;
    }

    &:focus-visible {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }
  }

  &__output {
    margin: 0.62rem 0 0;
    min-height: 220px;
    max-height: 380px;
    border-radius: 12px;
    border: 1px solid #d4e1f7;
    background: #ffffff;
    color: #0f172a;
    font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace;
    font-size: 0.94rem;
    padding: 0.75rem 0.82rem;
    line-height: 1.56;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
    overflow: auto;
  }

  &__output-wrap {
    position: relative;
  }

  &__spinner {
    position: absolute;
    right: 0.72rem;
    bottom: 0.72rem;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border: 1px solid #c8dbf7;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.95);
    color: #1d4ed8;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.26rem 0.5rem;
    backdrop-filter: blur(2px);
  }

  &__spinner-ring {
    width: 13px;
    height: 13px;
    border-radius: 999px;
    border: 2px solid rgba(59, 130, 246, 0.25);
    border-top-color: #2563eb;
    animation: hero-spin 720ms linear infinite;
  }

  &__actions {
    margin-top: 0.65rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  &__btn {
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 0.56rem 0.9rem;
    font-size: 0.88rem;
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
    color: #ffffff;
    border-color: rgba(67, 56, 202, 0.35);
    background: linear-gradient(145deg, #4f46e5, #2563eb);
    box-shadow: 0 12px 26px rgba(59, 130, 246, 0.34);

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 18px 32px rgba(59, 130, 246, 0.42);
    }
  }

  &__btn--secondary {
    color: #1d4ed8;
    border-color: #c9dcfa;
    background: linear-gradient(180deg, #ffffff, #eff6ff);
    box-shadow: 0 2px 12px rgba(59, 130, 246, 0.08);

    &:hover,
    &:focus-visible {
      background: #dbeafe;
      border-color: #93c5fd;
      transform: translateY(-1px);
      box-shadow: 0 10px 20px rgba(59, 130, 246, 0.16);
    }
  }

  &__btn--ghost {
    color: #475569;
    border-color: #d5e2f8;
    background: #ffffff;
    box-shadow: 0 1px 8px rgba(15, 23, 42, 0.05);

    &:hover,
    &:focus-visible {
      background: #f8fbff;
      border-color: #c3d7f5;
      transform: translateY(-1px);
    }
  }

  &__status {
    margin: 0.56rem 0 0;
    color: #2563eb;
    font-size: 0.82rem;
    font-weight: 600;
  }

  &__mode {
    margin-top: 0.58rem;
    display: inline-flex;
    gap: 0.4rem;
    padding: 0.24rem;
    border-radius: 12px;
    background: var(--surface-soft);
    border: 1px solid var(--border);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 10px;
    background: transparent;
    color: var(--text-muted);
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.36rem 0.66rem;
    cursor: pointer;
    transition: background 160ms ease, color 160ms ease, border-color 160ms ease;
  }

  &__mode-btn--active {
    color: var(--text);
    background: var(--surface);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-sm);
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
      max-width: 420px;
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
      border-radius: 20px;
      padding: 0.86rem;
    }

    &__demo {
      margin-top: 0.85rem;
      border-radius: 14px;
      padding: 0.62rem;
    }

    &__panel {
      border-radius: 12px;
      padding: 0.64rem;
    }

    &__lede {
      font-size: 0.95rem;
      line-height: 1.52;
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
  }
}
</style>
