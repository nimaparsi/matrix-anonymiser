<script setup lang="ts">
import { computed, ref, watch } from 'vue'

type TokenType = 'Person' | 'Organisation' | 'Email' | 'Phone' | 'Address'

const inputText = ref('')
const outputText = ref('')
const exampleText = [
  'John Smith from Acme emailed john@acme.com',
  'Call me on 07912345678',
].join('\n')

const hasInput = computed(() => inputText.value.trim().length > 0)

watch(
  inputText,
  (nextValue) => {
    outputText.value = anonymise(nextValue)
  },
  { immediate: true },
)

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

function applyExample() {
  inputText.value = exampleText
}

function clearDemo() {
  inputText.value = ''
}
</script>

<template>
  <section class="hero-demo" aria-labelledby="hero-title">
    <div class="hero-demo__copy">
      <p class="hero-demo__eyebrow">Private by design</p>
      <h1 id="hero-title">Sanitise sensitive text before AI sees it.</h1>
      <p>
        Create clean, safe-to-share prompts in seconds. Detect sensitive details and replace them with structured
        placeholders while preserving meaning.
      </p>
    </div>

    <article class="hero-demo__card" aria-label="Interactive anonymisation demo">
      <div class="hero-demo__card-grid">
        <div class="hero-demo__panel">
          <label class="hero-demo__label" for="demo-input">Paste your text</label>
          <textarea
            id="demo-input"
            v-model="inputText"
            class="hero-demo__textarea"
            placeholder="Paste text containing sensitive details..."
          ></textarea>
          <div class="hero-demo__actions">
            <button class="hero-demo__btn hero-demo__btn--primary" type="button" @click="applyExample">Try example</button>
            <button
              class="hero-demo__btn hero-demo__btn--ghost"
              type="button"
              :disabled="!hasInput"
              @click="clearDemo"
            >
              Clear
            </button>
          </div>
        </div>

        <div class="hero-demo__panel hero-demo__panel--output">
          <p class="hero-demo__label">Sanitised output</p>
          <pre class="hero-demo__output">{{ outputText || 'Sanitised output appears here.' }}</pre>
        </div>
      </div>
    </article>
  </section>
</template>

<style scoped lang="scss">
.hero-demo {
  &__copy {
    max-width: 760px;

    h1 {
      margin: 0.5rem 0 0;
      color: #0f172a;
      font-size: clamp(2rem, 5vw, 3.3rem);
      line-height: 1.08;
      letter-spacing: -0.03em;
    }

    p {
      margin: 1rem 0 0;
      color: #475569;
      font-size: 1.06rem;
      line-height: 1.58;
      max-width: 62ch;
    }
  }

  &__eyebrow {
    margin: 0;
    color: #1d4ed8;
    font-size: 0.84rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 700;
  }

  &__card {
    margin-top: 1.55rem;
    background: #ffffff;
    border-radius: 24px;
    border: 1px solid #dbe4f5;
    box-shadow: 0 22px 42px rgba(15, 23, 42, 0.08);
    padding: 1.2rem;
  }

  &__card-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }

  &__panel {
    border: 1px solid #dce6f8;
    border-radius: 18px;
    padding: 1rem;
    background: #fbfdff;
    min-height: 332px;
  }

  &__panel--output {
    background: #f8fbff;
  }

  &__label {
    display: block;
    margin: 0;
    color: #1e293b;
    font-size: 0.92rem;
    font-weight: 700;
    letter-spacing: 0.01em;
  }

  &__textarea {
    margin-top: 0.7rem;
    width: 100%;
    min-height: 210px;
    resize: vertical;
    border-radius: 14px;
    border: 1px solid #cddbf3;
    background: #ffffff;
    color: #0f172a;
    padding: 0.86rem 0.9rem;
    line-height: 1.55;
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
    margin: 0.7rem 0 0;
    min-height: 255px;
    border-radius: 14px;
    border: 1px solid #d6e2f7;
    background: #ffffff;
    color: #0f172a;
    padding: 0.86rem 0.9rem;
    line-height: 1.58;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
  }

  &__actions {
    margin-top: 0.72rem;
    display: flex;
    align-items: center;
    gap: 0.55rem;
  }

  &__btn {
    border: 1px solid transparent;
    border-radius: 11px;
    padding: 0.56rem 0.9rem;
    font-size: 0.9rem;
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

  &__btn--ghost {
    color: #1e40af;
    border-color: #bfdbfe;
    background: #eff6ff;

    &:hover,
    &:focus-visible {
      background: #dbeafe;
      border-color: #93c5fd;
    }
  }
}

@media (max-width: 900px) {
  .hero-demo {
    &__copy {
      p {
        font-size: 1rem;
      }
    }

    &__card {
      margin-top: 1.2rem;
      padding: 0.9rem;
    }

    &__card-grid {
      grid-template-columns: 1fr;
      gap: 0.8rem;
    }

    &__panel {
      min-height: 0;
    }

    &__textarea,
    &__output {
      min-height: 180px;
    }
  }
}

</style>
