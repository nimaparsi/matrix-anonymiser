<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { PhArrowRight, PhChecks, PhEnvelopeSimple } from '@phosphor-icons/vue'

const route = useRoute()
const formSectionRef = ref<HTMLElement | null>(null)

const topics = ['General enquiry', 'Support request', 'Security review', 'Enterprise contact', 'Partnership']

const form = reactive({
  name: '',
  email: '',
  company: '',
  topic: 'General enquiry',
  message: '',
})

function normalizeTopic(raw: string) {
  return raw.toLowerCase().replace(/[^a-z0-9]+/g, '-')
}

const topicMap = Object.fromEntries(topics.map((topic) => [normalizeTopic(topic), topic]))

const preselectedTopic = computed(() => {
  const queryTopic = String(route.query.topic || '')
  return topicMap[normalizeTopic(queryTopic)] || null
})

watch(
  preselectedTopic,
  (value) => {
    if (value) form.topic = value
  },
  { immediate: true },
)

const isSending = ref(false)
const formStatus = reactive<{ kind: 'idle' | 'success' | 'error'; message: string }>({
  kind: 'idle',
  message: '',
})

const canSubmit = computed(() => {
  return !!form.name.trim() && !!form.email.trim() && !!form.message.trim() && !isSending.value
})

function toSafeContactErrorMessage(raw: unknown) {
  const text = String(raw || '').trim()
  if (!text) return 'Unable to send message right now. Please try again shortly.'

  const normalized = text.toLowerCase()
  const leakedConfigHints = ['resend_api_key', 'contact service not configured', 'missing resend']
  if (leakedConfigHints.some((hint) => normalized.includes(hint))) {
    return 'Unable to send message right now. Please try again shortly.'
  }

  return text
}

function jumpToForm(topic: string) {
  form.topic = topic
  nextTick(() => {
    formSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

async function submitContact() {
  if (!canSubmit.value) {
    formStatus.kind = 'error'
    formStatus.message = 'Please add your name, email, and message.'
    return
  }

  isSending.value = true
  formStatus.kind = 'idle'
  formStatus.message = ''

  try {
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: form.name.trim(),
        email: form.email.trim(),
        company: form.company.trim(),
        topic: form.topic,
        message: form.message.trim(),
      }),
    })

    const contentType = response.headers.get('content-type') || ''
    const payload = contentType.includes('application/json') ? await response.json().catch(() => ({})) : {}
    if (!response.ok) {
      const safeDetail = typeof payload?.detail === 'string'
        ? toSafeContactErrorMessage(payload.detail)
        : response.status >= 500
          ? 'Unable to send message right now. Please try again shortly.'
          : response.status === 404
            ? 'Contact route is not available right now. Please try again shortly.'
            : 'Unable to send message right now.'
      throw new Error(safeDetail)
    }

    formStatus.kind = 'success'
    formStatus.message = 'Message sent. We will get back to you shortly.'
    form.message = ''
  } catch (error) {
    formStatus.kind = 'error'
    formStatus.message = toSafeContactErrorMessage(
      error instanceof Error && error.message
        ? error.message
        : 'Unable to reach contact service right now. Please try again shortly.',
    )

  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <main class="contact-page">
    <section class="contact-page__hero">
      <div class="contact-page__hero-copy">
        <p class="contact-page__eyebrow">
          <PhChecks :size="12" weight="duotone" aria-hidden="true" />
          Contact
        </p>
        <h1>
          Let’s build a safer<br />
          <span>sharing workflow.</span>
        </h1>
        <p>
          Reach out for product support, security questions, and rollout planning. We’ll help you move from raw text
          exposure to safe-to-share anonymised workflows.
        </p>

        <div class="contact-page__hero-actions">
          <button class="btn btn--primary" type="button" @click="jumpToForm('Support request')">
            <PhEnvelopeSimple :size="14" weight="bold" aria-hidden="true" />
            <span>Contact support</span>
          </button>
          <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Open Tool</RouterLink>
        </div>
      </div>
    </section>

    <section ref="formSectionRef" class="contact-page__grid">
      <article class="contact-page__card contact-page__card--form">
        <header>
          <h2>Send a message</h2>
          <p>Submit your request directly. Topic selection sets the email subject automatically.</p>
        </header>

        <form class="contact-page__form" @submit.prevent="submitContact">
          <div class="contact-page__fields">
            <label>
              <span>Name</span>
              <input v-model="form.name" type="text" autocomplete="name" placeholder="Jane Doe" />
            </label>
            <label>
              <span>Email</span>
              <input v-model="form.email" type="email" autocomplete="email" placeholder="jane@company.com" />
            </label>
            <label>
              <span>Company</span>
              <input v-model="form.company" type="text" autocomplete="organization" placeholder="Acme Labs" />
            </label>
            <label>
              <span>Topic</span>
              <select v-model="form.topic">
                <option v-for="topic in topics" :key="topic" :value="topic">{{ topic }}</option>
              </select>
            </label>
          </div>

          <label class="contact-page__message">
            <span>Message</span>
            <textarea
              v-model="form.message"
              rows="7"
              placeholder="Tell us what you’re trying to sanitise and where you need help."
            ></textarea>
          </label>

          <div class="contact-page__form-actions">
            <button class="btn btn--primary" type="submit" :disabled="!canSubmit">
              <span>{{ isSending ? 'Sending...' : 'Send message' }}</span>
              <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
            </button>
            <button class="btn btn--ghost" type="button" @click="jumpToForm('Enterprise contact')">
              Enterprise contact
            </button>
          </div>

          <p v-if="formStatus.message" class="contact-page__status" :class="`contact-page__status--${formStatus.kind}`">
            {{ formStatus.message }}
          </p>
        </form>
      </article>

      <article class="contact-page__card contact-page__card--faq">
        <h3>What can we help with?</h3>
        <ul>
          <li>
            <strong>Security review</strong>
            <p>Understand data flow, local-first processing, and practical controls.</p>
          </li>
          <li>
            <strong>Rollout support</strong>
            <p>Plan how teams can sanitize notes, contracts, and prompt drafts safely.</p>
          </li>
          <li>
            <strong>Product questions</strong>
            <p>Clarify current capabilities and near-term roadmap direction.</p>
          </li>
        </ul>
      </article>
    </section>
  </main>
</template>

<style scoped lang="scss">
.contact-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.2rem;

  &__hero {
    display: block;
  }

  &__hero-copy {
    max-width: 760px;

    h1 {
      margin: 0.72rem 0 0;
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(2.8rem, 6vw, 5rem);
      line-height: 0.93;
      letter-spacing: -0.05em;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 1rem 0 0;
      max-width: 50ch;
      color: var(--text-2);
      font-size: 1rem;
      line-height: 1.62;
    }
  }

  &__eyebrow {
    margin: 0;
    display: inline-flex;
    align-items: center;
    gap: 0.34rem;
    border-radius: 999px;
    padding: 0.25rem 0.62rem;
    background: color-mix(in srgb, var(--accent-soft), white 34%);
    color: var(--accent-3);
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 76%);
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 760;
  }

  &__hero-actions {
    margin-top: 1.2rem;
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.56rem;

    .btn {
      min-height: 48px;
      padding-inline: 1rem;
    }
  }

  &__grid {
    margin-top: 1.6rem;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(300px, 0.74fr);
    gap: 0.9rem;
  }

  &__card {
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    box-shadow: var(--shadow-xs);
    padding: 1rem;
  }

  &__card--form header {
    h2 {
      margin: 0;
      font-size: 1.7rem;
      line-height: 1.1;
      letter-spacing: -0.03em;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0.52rem 0 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.55;
    }
  }

  &__form {
    margin-top: 0.82rem;
  }

  &__fields {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.56rem;
  }

  label {
    display: grid;
    gap: 0.34rem;

    span {
      color: var(--text-2);
      font-size: 0.67rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 760;
    }
  }

  input,
  select,
  textarea {
    appearance: none;
    width: 100%;
    border-radius: 10px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 18%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 50%);
    color: var(--text-1);
    font-size: 0.92rem;
    line-height: 1.5;
    transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
  }

  input,
  select {
    min-height: 44px;
    padding: 0.58rem 0.74rem;
  }

  textarea {
    padding: 0.68rem 0.74rem;
    resize: vertical;
    min-height: 150px;
  }

  input:focus-visible,
  select:focus-visible,
  textarea:focus-visible {
    outline: none;
    border-color: color-mix(in srgb, var(--accent-1), transparent 32%);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent-1), transparent 84%);
  }

  &__message {
    margin-top: 0.58rem;
  }

  &__form-actions {
    margin-top: 0.72rem;
    display: inline-flex;
    align-items: center;
    gap: 0.56rem;
    flex-wrap: wrap;
  }

  &__status {
    margin: 0.64rem 0 0;
    font-size: 0.84rem;
    font-weight: 640;
    line-height: 1.45;
  }

  &__status--success {
    color: #0f8a53;
  }

  &__status--error {
    color: #b42318;
  }

  &__card--faq {
    h3 {
      margin: 0;
      font-size: 1.35rem;
      line-height: 1.1;
      letter-spacing: -0.02em;
    }

    ul {
      margin: 0.76rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.58rem;
    }

    li {
      border-radius: 12px;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 42%);
      padding: 0.7rem;
    }

    strong {
      display: block;
      color: var(--text-1);
      font-size: 0.98rem;
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.35rem 0 0;
      color: var(--text-2);
      font-size: 0.84rem;
      line-height: 1.5;
    }
  }
}

@media (max-width: 980px) {
  .contact-page {
    width: min(1200px, calc(100% - 1rem));

    &__hero,
    &__grid,
    &__fields {
      grid-template-columns: 1fr;
    }
  }
}
</style>
