<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { PhBroom, PhClipboardText, PhCopySimple, PhSparkle } from '@phosphor-icons/vue'

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
  instant?: boolean
  focus?: boolean
}>

type OutputPart = {
  text: string
  tokenType?: TokenType
}

const TOKEN_PATTERN = /\[(Person|Organisation|Email|Phone|Address|ApiKey|IpAddress)\s+(\d+)\]/g

const inputText = ref('')
const outputText = ref('')
const copyLabel = ref('Copy output')
const statusMessage = ref('')
const isSanitising = ref(false)
const outputPulse = ref(false)
const lastSanitisedSignature = ref<string | null>(null)
const detectionMode = ref<'automatic' | 'custom'>('automatic')
const selectedTagKeys = ref<TokenType[]>(['Person', 'Organisation', 'Email', 'Phone', 'Address'])
const inputEl = ref<HTMLTextAreaElement | null>(null)

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
  defaultExampleText,
  [
    'Project Coordination Memo',
    'Prepared by: Anna Carter',
    'Organisation: Green Horizon Research',
    'Contact: anna.carter@example.com',
    'Phone: +44 7700 900123',
    'Address: 14 Willow Lane, Brighton',
  ].join('\n'),
  [
    'Support incident summary',
    'Reporter: Alice Morgan',
    'Email: alice.morgan@contoso.dev',
    'Phone: +44 7700 900456',
    'Host: 10.12.8.32',
    'API key: api_key=prod_9fH3mQ7xV2pL5rT8kN1dW4cY',
  ].join('\n'),
  [
    'Client proposal notes',
    'Consultant: Sofia Martinez',
    'Client: Urban Growth Initiative',
    'Email: sofia.martinez@urbangrowth.co.uk',
    'Dial-in: +44 7700 903876',
    'Venue: 55 Orchard Street, Manchester',
  ].join('\n'),
]

let lastGeneralExampleIndex = -1

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
  return `${inputText.value}\u0000${detectionMode.value}\u0000${enabledTags.join('|')}`
})

const needsSanitise = computed(() => {
  if (!hasInput.value) return false
  if (!hasOutput.value) return true
  return currentSanitiseSignature.value !== lastSanitisedSignature.value
})

const modeSummary = computed(() =>
  detectionMode.value === 'automatic' ? 'Automatic detection enabled' : `${selectedTagKeys.value.length} custom rules enabled`,
)

const previewStats = computed(() => {
  if (!hasInput.value) {
    return {
      count: 0,
      labels: [] as string[],
    }
  }
  const previewOutput = anonymise(inputText.value, enabledTagSet.value)
  const summary = extractTokenStats(previewOutput)
  return {
    count: summary.total,
    labels: summary.previewLabels,
  }
})

const sanitiseButtonLabel = computed(() => {
  if (isSanitising.value) return 'Sanitising…'
  if (hasInput.value && !needsSanitise.value) return 'Sanitised'
  if (previewStats.value.count > 0) return `Sanitise ${previewStats.value.count} items`
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
    transformed = transformed.replace(
      /\b(from|at|with)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\b/g,
      (full, connector: string, name: string) => {
        if (name.startsWith('[')) return full
        if (/^[A-Z][a-z]+\s+[A-Z][a-z]+$/.test(name)) return full
        return `${connector} ${tokenFor('Organisation', name)}`
      },
    )
  }

  if (enabledTags.has('Person')) {
    transformed = transformed.replace(/\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b/g, (match) => {
      if (match.startsWith('[')) return match
      return tokenFor('Person', match)
    })
  }

  return transformed
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

  return { total, counter, previewLabels }
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
  outputText.value = ''

  await new Promise<void>((resolve) => {
    sanitiseTimer = window.setTimeout(() => {
      sanitiseTimer = null
      resolve()
    }, SANITISE_SPINNER_MS)
  })

  outputText.value = anonymise(inputText.value, enabledTagSet.value)
  lastSanitisedSignature.value = currentSanitiseSignature.value
  copyLabel.value = 'Copy output'
  isSanitising.value = false
  triggerOutputPulse()
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

  if (generalExamples.length < 2) return generalExamples[0]

  let nextIndex = Math.floor(Math.random() * generalExamples.length)
  if (nextIndex === lastGeneralExampleIndex) {
    nextIndex = (nextIndex + 1) % generalExamples.length
  }
  lastGeneralExampleIndex = nextIndex
  return generalExamples[nextIndex]
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
        instant: true,
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

    if (detail.instant ?? true) {
      outputText.value = anonymise(inputText.value, enabledTagSet.value)
      lastSanitisedSignature.value = currentSanitiseSignature.value
      copyLabel.value = 'Copy output'
      triggerOutputPulse()
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
        <p class="hero__eyebrow">Private by design</p>
        <h1 id="hero-title">Sanitise sensitive data before it reaches AI</h1>
        <p class="hero__lede">
          Automatically detect and anonymise names, emails, phone numbers, addresses, invoice-style identifiers, and
          other sensitive details before sharing text with AI tools, documents, or teammates.
        </p>
        <p class="hero__risk">Most AI tools do not anonymise sensitive data for you.</p>
        <div class="hero__trust">
          <span>No data stored</span>
          <span>Instant processing</span>
          <span>Privacy-first</span>
        </div>
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
            <div v-if="previewStats.count > 0" class="hero__live-detect" role="status" aria-live="polite">
              <strong>Sensitive entities detected: {{ previewStats.count }}</strong>
              <span>{{ previewStats.labels.join(' · ') }}</span>
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
            {{ modeSummary }}<span v-if="previewStats.labels.length"> · {{ previewStats.labels.join(' · ') }}</span>
          </p>

          <div class="hero__output-wrap">
            <div class="hero__output">
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
    align-items: end;
    gap: 1rem;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
    font-weight: 700;
  }

  h1 {
    margin-top: 0.62rem;
    max-width: 18ch;
    font-size: clamp(2.2rem, 5.6vw, 4rem);
    line-height: 0.98;
    letter-spacing: -0.04em;
  }

  &__lede {
    margin: 0.9rem 0 0;
    max-width: 64ch;
    color: var(--text-2);
    font-size: clamp(1rem, 1.8vw, 1.12rem);
    line-height: 1.62;
  }

  &__risk {
    margin: 0.62rem 0 0;
    color: color-mix(in srgb, var(--text-2), var(--accent-1) 24%);
    font-size: 0.95rem;
    font-weight: 600;
  }

  &__trust {
    margin-top: 0.72rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.46rem;

    span {
      border: 1px solid color-mix(in srgb, var(--border-2), transparent 10%);
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 20%);
      padding: 0.28rem 0.58rem;
      font-size: 0.77rem;
      color: var(--text-2);
      font-weight: 600;
    }
  }

  &__try {
    margin-top: 0.9rem;
    min-height: 46px;
    padding-inline: 1.08rem;
  }

  &__mascot {
    width: clamp(142px, 18vw, 206px);
    aspect-ratio: 420 / 301;
    object-fit: cover;
    object-position: center;
    border-radius: 16px;
    box-shadow: var(--shadow-sm);
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 18%);
  }

  &__demo {
    margin-top: 1.45rem;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 6%);
    border-radius: var(--radius-xl);
    background: var(--surface-0);
    box-shadow: var(--shadow-lg);
    padding: clamp(1rem, 2.4vw, 1.4rem);
  }

  &__demo-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 0.9rem;
    margin-bottom: 0.96rem;
  }

  &__demo-title {
    margin: 0;
    font-size: 1.18rem;
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
    gap: 0.46rem;

    .btn {
      min-height: 40px;
      padding-inline: 0.86rem;
    }
  }

  &__demo-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 1rem;
  }

  &__panel {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 6%);
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-1), white 35%);
    min-height: 392px;
    padding: 0.92rem;
    box-shadow: var(--shadow-sm);
  }

  &__panel--output {
    background: color-mix(in srgb, var(--surface-1), var(--accent-soft) 28%);
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
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 20%);
    border-radius: 999px;
    background: var(--surface-0);
    color: var(--text-2);
    min-height: 34px;
    padding: 0.28rem 0.56rem;
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
    margin-top: 0.66rem;
    width: 100%;
    min-height: 210px;
    max-height: 500px;
    resize: none;
    border-radius: var(--radius-md);
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 8%);
    background: var(--surface-0);
    color: var(--text-1);
    padding: 0.9rem;
    font-size: 0.96rem;
    line-height: 1.68;
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
    margin-top: 0.72rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.6rem;
  }

  &__live-detect {
    display: grid;
    gap: 0.15rem;

    strong {
      color: var(--text-1);
      font-size: 0.83rem;
      font-weight: 700;
    }

    span {
      color: var(--text-3);
      font-size: 0.78rem;
    }
  }

  &__sanitise {
    min-width: 174px;
    min-height: 44px;
  }

  &__options {
    margin-top: 0.74rem;
    display: grid;
    gap: 0.62rem;
  }

  &__mode {
    width: fit-content;
    max-width: 100%;
    display: inline-grid;
    grid-template-columns: auto auto;
    gap: 0.28rem;
    padding: 0.22rem;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 10%);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-2), transparent 18%);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 10px;
    background: transparent;
    color: var(--text-2);
    font-size: 0.81rem;
    font-weight: 600;
    padding: 0.44rem 0.72rem;
    cursor: pointer;
    transition: color 180ms ease, background 180ms ease, border-color 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
    }
  }

  &__mode-btn--active {
    color: var(--text-1);
    background: var(--surface-0);
    border-color: color-mix(in srgb, var(--border-2), transparent 14%);
    box-shadow: var(--shadow-xs);
  }

  &__tag-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.46rem;
  }

  &__tag-chip {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: 12px;
    background: var(--surface-0);
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
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: var(--radius-md);
    background: var(--surface-0);
    min-height: 298px;
    max-height: 500px;
    overflow: auto;
    padding: 1rem;
    font-size: 0.97rem;
    line-height: 1.72;
    color: var(--text-1);
    transition: background 240ms ease;
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
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 58%);
    background: color-mix(in srgb, var(--accent-soft), white 46%);
    color: color-mix(in srgb, var(--accent-3), black 12%);
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.86rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    padding: 0.12rem 0.5rem;
    margin: 0.04rem 0.15rem;
    animation: token-flash 320ms ease;
  }

  &__token--person {
    background: color-mix(in srgb, #dbeafe, white 44%);
  }

  &__token--organisation {
    background: color-mix(in srgb, #d1fae5, white 40%);
  }

  &__token--email {
    background: color-mix(in srgb, #e0e7ff, white 38%);
  }

  &__token--phone {
    background: color-mix(in srgb, #fef3c7, white 40%);
  }

  &__token--address {
    background: color-mix(in srgb, #fee2e2, white 44%);
  }

  &__token--apikey,
  &__token--ipaddress {
    background: color-mix(in srgb, #ede9fe, white 38%);
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
    filter: brightness(1.2);
  }
  to {
    filter: brightness(1);
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
