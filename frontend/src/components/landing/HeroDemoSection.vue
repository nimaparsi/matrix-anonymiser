<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'

type TokenType = 'Person' | 'Organisation' | 'Email' | 'Phone' | 'Address'

const inputText = ref('')
const outputText = ref('')
const copyLabel = ref('Copy output')
const statusMessage = ref('')
let statusTimer: ReturnType<typeof window.setTimeout> | null = null

const exampleText = [
  'John Smith from Acme emailed john@acme.com',
  'Call me on 07912345678',
].join('\n')

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
  }

  const tokenCounts: Record<TokenType, number> = {
    Person: 0,
    Organisation: 0,
    Email: 0,
    Phone: 0,
    Address: 0,
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

function sanitiseNow() {
  outputText.value = anonymise(inputText.value)
  copyLabel.value = 'Copy output'
}

function applyExample() {
  inputText.value = exampleText
  sanitiseNow()
  setStatus('Example loaded')
}

function clearDemo() {
  inputText.value = ''
  outputText.value = ''
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
    sanitiseNow()
  }
}

onUnmounted(() => {
  if (statusTimer) {
    window.clearTimeout(statusTimer)
    statusTimer = null
  }
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
              v-model="inputText"
              class="hero__textarea"
              placeholder="Paste text containing sensitive details..."
              @keydown="handleInputKeydown"
            ></textarea>
            <div class="hero__actions">
              <button class="hero__btn hero__btn--primary" type="button" :disabled="!hasInput" @click="sanitiseNow">Sanitise text</button>
              <button class="hero__btn hero__btn--secondary" type="button" @click="applyExample">Try example</button>
              <button class="hero__btn hero__btn--ghost" type="button" :disabled="!hasInput" @click="clearDemo">Clear</button>
            </div>
            <p v-if="statusMessage" class="hero__status" role="status" aria-live="polite">{{ statusMessage }}</p>
          </section>

          <section class="hero__panel hero__panel--output">
            <div class="hero__panel-top">
              <p class="hero__label">Sanitised output</p>
              <button class="hero__chip" type="button" :disabled="!hasOutput" @click="copyOutput">{{ copyLabel }}</button>
            </div>
            <pre class="hero__output">{{ outputText || 'Sanitised output appears here.' }}</pre>
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
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.32rem 0.58rem;
    cursor: pointer;
    transition: background 160ms ease, border-color 160ms ease;

    &:hover,
    &:focus-visible {
      background: #dbeafe;
      border-color: #93c5fd;
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
    resize: vertical;
    border-radius: 12px;
    border: 1px solid #ccdbf2;
    background: #ffffff;
    color: #0f172a;
    padding: 0.75rem 0.82rem;
    line-height: 1.56;
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
    border-radius: 12px;
    border: 1px solid #d4e1f7;
    background: #ffffff;
    color: #0f172a;
    padding: 0.75rem 0.82rem;
    line-height: 1.56;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
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
    border-radius: 11px;
    padding: 0.52rem 0.82rem;
    font-size: 0.88rem;
    font-weight: 700;
    cursor: pointer;
    transition: transform 160ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;

    &:disabled {
      opacity: 0.58;
      cursor: not-allowed;
    }
  }

  &__btn--primary {
    color: #ffffff;
    background: linear-gradient(145deg, #2563eb, #4338ca);
    box-shadow: 0 10px 24px rgba(59, 130, 246, 0.3);

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 14px 28px rgba(59, 130, 246, 0.34);
    }
  }

  &__btn--secondary {
    color: #1e40af;
    border-color: #bfdbfe;
    background: #eff6ff;

    &:hover,
    &:focus-visible {
      background: #dbeafe;
      border-color: #93c5fd;
    }
  }

  &__btn--ghost {
    color: #475569;
    border-color: #d5e2f8;
    background: #ffffff;

    &:hover,
    &:focus-visible {
      background: #f8fbff;
      border-color: #c3d7f5;
    }
  }

  &__status {
    margin: 0.56rem 0 0;
    color: #2563eb;
    font-size: 0.82rem;
    font-weight: 600;
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
  }
}
</style>
