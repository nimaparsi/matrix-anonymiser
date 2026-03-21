<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  PhCheckCircle,
  PhCopy,
  PhDownloadSimple,
  PhEraser,
  PhMagicWand,
  PhShieldCheck,
  PhSparkle,
} from '@phosphor-icons/vue'
import {
  TOOL_EXAMPLE_INPUT,
  defaultDetectorState,
  sanitiseText,
  splitOutputByTokens,
  type DetectorKey,
  type SanitiseResult,
  type TokenType,
} from '../lib/sanitiser'

const route = useRoute()

const inputText = ref('')
const outputText = ref('')
const inputRef = ref<HTMLTextAreaElement | null>(null)
const isProcessing = ref(false)
const copyLabel = ref('Copy result')
const mode = ref<'automatic' | 'custom'>('automatic')
const detectorState = ref(defaultDetectorState())
const result = ref<SanitiseResult | null>(null)
const statusText = ref('')
const lastSignature = ref('')

const detectorOptions: Array<{ key: DetectorKey; label: string }> = [
  { key: 'person', label: 'Names' },
  { key: 'organisation', label: 'Organisations' },
  { key: 'email', label: 'Emails' },
  { key: 'phone', label: 'Phone numbers' },
  { key: 'address', label: 'Addresses' },
  { key: 'invoice', label: 'Invoice IDs' },
  { key: 'ip', label: 'IP addresses' },
  { key: 'secret', label: 'Secret keys' },
  { key: 'username', label: 'Usernames' },
]

const activeDetectors = computed<Record<DetectorKey, boolean>>(() => {
  if (mode.value === 'automatic') {
    return defaultDetectorState()
  }
  return detectorState.value
})

const signature = computed(() => `${inputText.value}::${mode.value}::${JSON.stringify(activeDetectors.value)}`)
const hasInput = computed(() => inputText.value.trim().length > 0)
const hasOutput = computed(() => outputText.value.trim().length > 0)
const needsSanitise = computed(() => hasInput.value && signature.value !== lastSignature.value)

const renderedLines = computed(() => {
  if (!outputText.value) return [] as Array<Array<{ text: string; tokenType?: TokenType }>>
  return outputText.value.split('\n').map((line) => splitOutputByTokens(line))
})

const detectedSummary = computed(() => {
  if (!result.value || result.value.total === 0) return 'No sensitive entities detected.'
  return `${result.value.total} entities detected`
})

const ctaLabel = computed(() => {
  if (isProcessing.value) return 'Sanitising...'
  if (!hasInput.value) return 'Paste text to sanitise'
  if (!needsSanitise.value) return 'Sanitised'
  return 'Sanitise text'
})

function tokenClass(type: TokenType) {
  return `tool-page__token--${type.toLowerCase()}`
}

function setInputFocus() {
  nextTick(() => {
    inputRef.value?.focus()
    const length = inputText.value.length
    inputRef.value?.setSelectionRange(length, length)
  })
}

function clearAll() {
  inputText.value = ''
  outputText.value = ''
  result.value = null
  statusText.value = ''
  copyLabel.value = 'Copy result'
  lastSignature.value = ''
  setInputFocus()
}

function applyExample(autoSanitise = true) {
  inputText.value = TOOL_EXAMPLE_INPUT
  if (autoSanitise) {
    void runSanitise()
  }
  setInputFocus()
}

function toggleDetector(key: DetectorKey) {
  detectorState.value[key] = !detectorState.value[key]
}

async function runSanitise() {
  if (!hasInput.value) return

  isProcessing.value = true
  await new Promise((resolve) => setTimeout(resolve, 260))

  const sanitised = sanitiseText(inputText.value, activeDetectors.value)
  outputText.value = sanitised.output
  result.value = sanitised
  lastSignature.value = signature.value
  statusText.value = sanitised.total > 0 ? `${sanitised.total} entities anonymised` : 'No sensitive entities detected'
  copyLabel.value = 'Copy result'
  isProcessing.value = false
}

async function copyOutput() {
  if (!hasOutput.value) return
  await navigator.clipboard.writeText(outputText.value)
  copyLabel.value = 'Copied'
  window.setTimeout(() => {
    copyLabel.value = 'Copy result'
  }, 1400)
}

function exportText() {
  if (!hasOutput.value) return
  const blob = new Blob([outputText.value], { type: 'text/plain;charset=utf-8' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'sanitised-output.txt'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

function maybeRunDemoFromQuery() {
  if (route.query.demo === '1') {
    applyExample(true)
  }
}

watch(
  () => route.query.demo,
  () => {
    maybeRunDemoFromQuery()
  },
)

onMounted(() => {
  maybeRunDemoFromQuery()
  setInputFocus()
})
</script>

<template>
  <main class="tool-page">
    <section class="tool-page__hero">
      <p class="tool-page__eyebrow">Sanitiser Tool (MVP)</p>
      <h1>Protect sensitive text before sharing</h1>
      <p>
        Paste text, detect sensitive entities, sanitise output, then copy or export. All current functionality remains
        active in this MVP workspace.
      </p>
    </section>

    <section class="tool-page__workspace" aria-label="Sanitiser workspace">
      <article class="tool-page__panel tool-page__panel--input">
        <header class="tool-page__panel-head">
          <div>
            <p>Original text</p>
            <small>Paste source content</small>
          </div>
          <button class="btn btn--secondary" type="button" @click="applyExample(true)">
            <PhSparkle :size="16" weight="duotone" aria-hidden="true" />
            <span>Try example</span>
          </button>
        </header>

        <textarea
          ref="inputRef"
          v-model="inputText"
          class="tool-page__textarea"
          placeholder="Paste sensitive text, logs, contracts, prompts, or notes..."
          @keydown.meta.enter.prevent="runSanitise"
          @keydown.ctrl.enter.prevent="runSanitise"
        ></textarea>

        <div class="tool-page__controls">
          <div class="tool-page__mode">
            <button
              type="button"
              class="tool-page__mode-btn"
              :class="{ 'tool-page__mode-btn--active': mode === 'automatic' }"
              @click="mode = 'automatic'"
            >
              Automatic
            </button>
            <button
              type="button"
              class="tool-page__mode-btn"
              :class="{ 'tool-page__mode-btn--active': mode === 'custom' }"
              @click="mode = 'custom'"
            >
              Custom rules
            </button>
          </div>

          <div v-if="mode === 'custom'" class="tool-page__detectors">
            <button
              v-for="item in detectorOptions"
              :key="item.key"
              type="button"
              class="tool-page__detector"
              :class="{ 'tool-page__detector--active': detectorState[item.key] }"
              @click="toggleDetector(item.key)"
            >
              <span>{{ item.label }}</span>
            </button>
          </div>

          <div class="tool-page__actions">
            <button class="btn btn--ghost" type="button" :disabled="!hasInput || isProcessing" @click="clearAll">
              <PhEraser :size="16" weight="duotone" aria-hidden="true" />
              <span>Clear</span>
            </button>
            <button
              class="btn btn--primary"
              type="button"
              :disabled="!hasInput || isProcessing || !needsSanitise"
              @click="runSanitise"
            >
              <PhMagicWand :size="16" weight="fill" aria-hidden="true" />
              <span>{{ ctaLabel }}</span>
            </button>
          </div>
        </div>
      </article>

      <article class="tool-page__panel tool-page__panel--output">
        <header class="tool-page__panel-head">
          <div>
            <p>Sanitised output</p>
            <small>{{ detectedSummary }}</small>
          </div>
          <div class="tool-page__panel-buttons">
            <button class="btn btn--secondary" type="button" :disabled="!hasOutput || isProcessing" @click="copyOutput">
              <PhCopy :size="16" weight="duotone" aria-hidden="true" />
              <span>{{ copyLabel }}</span>
            </button>
            <button class="btn btn--secondary" type="button" :disabled="!hasOutput || isProcessing" @click="exportText">
              <PhDownloadSimple :size="16" weight="duotone" aria-hidden="true" />
              <span>Export .txt</span>
            </button>
          </div>
        </header>

        <div class="tool-page__output-shell">
          <div class="tool-page__output">
            <template v-if="renderedLines.length">
              <p v-for="(line, lineIndex) in renderedLines" :key="lineIndex" class="tool-page__line">
                <template v-for="(part, partIndex) in line" :key="`${lineIndex}-${partIndex}`">
                  <span v-if="part.tokenType" class="tool-page__token" :class="tokenClass(part.tokenType)">{{ part.text }}</span>
                  <span v-else>{{ part.text }}</span>
                </template>
              </p>
            </template>
            <p v-else class="tool-page__placeholder">Sanitised output appears here after you run the tool.</p>
          </div>

          <div v-if="isProcessing" class="tool-page__spinner" role="status" aria-live="polite">
            <span class="tool-page__spinner-ring" aria-hidden="true"></span>
            <span>Processing</span>
          </div>
        </div>

        <footer v-if="result && result.detectedLabels.length" class="tool-page__summary">
          <PhShieldCheck :size="16" weight="fill" aria-hidden="true" />
          <ul>
            <li v-for="label in result.detectedLabels" :key="label">{{ label }}</li>
          </ul>
        </footer>

        <footer v-else-if="statusText" class="tool-page__summary tool-page__summary--empty">
          <PhCheckCircle :size="16" weight="duotone" aria-hidden="true" />
          <p>{{ statusText }}</p>
        </footer>
      </article>
    </section>
  </main>
</template>

<style scoped lang="scss">
.tool-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 1.9rem;

  &__hero {
    max-width: 72ch;

    h1 {
      margin-top: 0.78rem;
      font-size: clamp(2.4rem, 5.6vw, 4.1rem);
      line-height: 0.95;
      letter-spacing: -0.045em;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0.96rem 0 0;
      color: var(--text-2);
      line-height: 1.63;
      font-size: 1rem;
    }
  }

  &__eyebrow {
    margin: 0;
    font-size: 0.66rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent-1);
    font-weight: 760;
  }

  &__workspace {
    margin-top: 1.4rem;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 0.84rem;
  }

  &__panel {
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 44%);
    box-shadow: var(--shadow-sm);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    min-height: 640px;
  }

  &__panel--output {
    background:
      radial-gradient(140% 110% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 56%), transparent 58%),
      color-mix(in srgb, var(--surface-0), var(--surface-1) 24%);
  }

  &__panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.7rem;

    p {
      margin: 0;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.13em;
      color: var(--text-2);
      font-weight: 760;
    }

    small {
      color: var(--text-3);
      font-size: 0.8rem;
      font-weight: 620;
    }
  }

  &__panel-buttons {
    display: inline-flex;
    gap: 0.44rem;

    .btn {
      min-height: 40px;
      padding-inline: 0.74rem;
      font-size: 0.82rem;
    }
  }

  &__textarea {
    margin-top: 0.8rem;
    width: 100%;
    min-height: 320px;
    flex: 1;
    resize: vertical;
    border-radius: 12px;
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 52%);
    color: var(--text-1);
    padding: 0.92rem 1rem;
    font-size: 0.94rem;
    line-height: 1.66;

    &:focus-visible {
      outline: none;
      border-color: color-mix(in srgb, var(--accent-2), transparent 18%);
      box-shadow: var(--ring);
    }
  }

  &__controls {
    margin-top: 0.82rem;
    display: grid;
    gap: 0.62rem;
  }

  &__mode {
    width: fit-content;
    max-width: 100%;
    display: inline-grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.25rem;
    padding: 0.24rem;
    border-radius: 10px;
    background: color-mix(in srgb, var(--surface-2), white 24%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 8px;
    background: transparent;
    color: var(--text-3);
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.44rem 0.64rem;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, border-color 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
    }
  }

  &__mode-btn--active {
    color: var(--text-1);
    border-color: color-mix(in srgb, var(--border-2), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 10%);
    box-shadow: var(--shadow-xs);
  }

  &__detectors {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.42rem;
  }

  &__detector {
    border-radius: 9px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 38%);
    padding: 0.4rem 0.5rem;
    text-align: left;
    cursor: pointer;
    color: var(--text-2);
    font-size: 0.76rem;
    font-weight: 650;
    transition: border-color 180ms ease, background 180ms ease;
  }

  &__detector--active {
    border-color: color-mix(in srgb, var(--accent-2), transparent 44%);
    background: color-mix(in srgb, var(--accent-soft), white 56%);
    color: var(--accent-3);
  }

  &__actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.58rem;

    .btn {
      min-height: 44px;
    }
  }

  &__output-shell {
    margin-top: 0.76rem;
    position: relative;
    flex: 1;
  }

  &__output {
    border-radius: 12px;
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 42%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 54%);
    padding: 1rem;
    min-height: 390px;
    max-height: 560px;
    overflow: auto;
    color: var(--text-1);
    font-size: 0.94rem;
    line-height: 1.72;
  }

  &__line {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }

  &__placeholder {
    margin: 0;
    color: var(--text-3);
    font-size: 0.9rem;
  }

  &__token {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid transparent;
    padding: 0.15rem 0.58rem;
    margin: 0.04rem 0.14rem;
    white-space: nowrap;
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.83rem;
    font-weight: 720;
    letter-spacing: -0.01em;
  }

  &__token--person {
    background: color-mix(in srgb, #dbeafe, white 26%);
    border-color: color-mix(in srgb, #3b82f6, transparent 42%);
    color: color-mix(in srgb, #1d4ed8, black 8%);
  }

  &__token--organisation {
    background: color-mix(in srgb, #ede9fe, white 20%);
    border-color: color-mix(in srgb, #8b5cf6, transparent 40%);
    color: color-mix(in srgb, #6d28d9, black 8%);
  }

  &__token--email {
    background: color-mix(in srgb, #dbeafe, white 32%);
    border-color: color-mix(in srgb, #2563eb, transparent 40%);
    color: color-mix(in srgb, #1e40af, black 8%);
  }

  &__token--phone {
    background: color-mix(in srgb, #cffafe, white 32%);
    border-color: color-mix(in srgb, #0891b2, transparent 42%);
    color: color-mix(in srgb, #155e75, black 8%);
  }

  &__token--address {
    background: color-mix(in srgb, #dcfce7, white 34%);
    border-color: color-mix(in srgb, #16a34a, transparent 42%);
    color: color-mix(in srgb, #166534, black 10%);
  }

  &__token--ip,
  &__token--secret,
  &__token--invoice,
  &__token--username {
    background: color-mix(in srgb, #fee2e2, white 28%);
    border-color: color-mix(in srgb, #dc2626, transparent 46%);
    color: color-mix(in srgb, #991b1b, black 6%);
  }

  &__spinner {
    position: absolute;
    right: 0.7rem;
    bottom: 0.7rem;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 48%);
    background: color-mix(in srgb, var(--surface-0), white 8%);
    padding: 0.24rem 0.52rem;
    color: var(--accent-3);
    font-size: 0.75rem;
    font-weight: 700;
  }

  &__spinner-ring {
    width: 11px;
    height: 11px;
    border-radius: 999px;
    border: 2px solid color-mix(in srgb, var(--accent-2), transparent 76%);
    border-top-color: var(--accent-2);
    animation: spin 680ms linear infinite;
  }

  &__summary {
    margin-top: 0.76rem;
    border-radius: 10px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 42%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
    padding: 0.56rem 0.68rem;
    display: flex;
    align-items: center;
    gap: 0.52rem;

    svg {
      color: var(--accent-1);
      flex-shrink: 0;
    }

    ul {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.42rem;

      li {
        border-radius: 999px;
        background: color-mix(in srgb, var(--accent-soft), white 44%);
        color: var(--accent-3);
        padding: 0.2rem 0.48rem;
        font-size: 0.72rem;
        font-weight: 760;
      }
    }

    p {
      margin: 0;
      color: var(--text-2);
      font-size: 0.83rem;
      font-weight: 650;
    }
  }

  &__summary--empty {
    background: color-mix(in srgb, var(--surface-1), white 6%);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1100px) {
  .tool-page {
    width: min(1200px, calc(100% - 1rem));

    &__workspace {
      grid-template-columns: 1fr;
    }

    &__panel {
      min-height: 0;
    }

    &__detectors {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
}

@media (max-width: 680px) {
  .tool-page {
    &__panel {
      padding: 0.8rem;
    }

    &__panel-head {
      flex-direction: column;
      align-items: flex-start;
    }

    &__panel-buttons {
      width: 100%;

      .btn {
        flex: 1;
      }
    }

    &__mode {
      width: 100%;
    }

    &__detectors {
      grid-template-columns: 1fr;
    }

    &__actions {
      .btn {
        flex: 1;
      }
    }
  }
}
</style>
