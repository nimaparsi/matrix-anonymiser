<script setup lang="ts">
import { computed, reactive } from 'vue'
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhChecks, PhEnvelopeSimple, PhHeadset, PhShieldCheck } from '@phosphor-icons/vue'

const form = reactive({
  name: '',
  email: '',
  company: '',
  topic: 'General',
  message: '',
})

const mailtoHref = computed(() => {
  const subject = `[SanitiseAI] ${form.topic} request`
  const body = [
    `Name: ${form.name || '-'}`,
    `Email: ${form.email || '-'}`,
    `Company: ${form.company || '-'}`,
    '',
    form.message || 'Please share more details about your request.',
  ].join('\n')

  return `mailto:nimaparsi@icloud.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
})

function openDraft() {
  window.location.href = mailtoHref.value
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
          <a class="btn btn--primary" href="mailto:nimaparsi@icloud.com">
            <PhEnvelopeSimple :size="14" weight="bold" aria-hidden="true" />
            <span>Email support</span>
          </a>
          <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Open Tool</RouterLink>
        </div>
      </div>

      <aside class="contact-page__hero-panel" aria-label="Contact channels">
        <article>
          <span><PhHeadset :size="16" weight="duotone" aria-hidden="true" /> General support</span>
          <strong>nimaparsi@icloud.com</strong>
          <small>Typical response: within 1 business day</small>
        </article>
        <article>
          <span><PhShieldCheck :size="16" weight="duotone" aria-hidden="true" /> Security & compliance</span>
          <strong>Security architecture questions</strong>
          <small>Share your requirements and we’ll respond with practical guidance.</small>
        </article>
      </aside>
    </section>

    <section class="contact-page__grid">
      <article class="contact-page__card contact-page__card--form">
        <header>
          <h2>Send a message</h2>
          <p>Draft your request below and open your email client with all details prefilled.</p>
        </header>

        <form class="contact-page__form" @submit.prevent="openDraft">
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
                <option>General</option>
                <option>Support</option>
                <option>Security</option>
                <option>Partnership</option>
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
            <button class="btn btn--primary" type="submit">
              <span>Open Email Draft</span>
              <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
            </button>
            <a class="btn btn--ghost" :href="mailtoHref">Use your mail client directly</a>
          </div>
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
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(320px, 0.84fr);
    gap: 1rem;
    align-items: stretch;
  }

  &__hero-copy {
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

  &__hero-panel {
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 28%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 22%);
    box-shadow: var(--shadow-sm);
    padding: 0.92rem;
    display: grid;
    gap: 0.62rem;

    article {
      border-radius: 12px;
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 44%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
      padding: 0.8rem;
    }

    span {
      display: inline-flex;
      align-items: center;
      gap: 0.34rem;
      color: var(--text-2);
      font-size: 0.68rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 740;
    }

    strong {
      display: block;
      margin-top: 0.4rem;
      color: var(--text-1);
      font-size: 1.06rem;
      letter-spacing: -0.02em;
      line-height: 1.24;
    }

    small {
      display: block;
      margin-top: 0.3rem;
      color: var(--text-3);
      font-size: 0.78rem;
      line-height: 1.5;
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
