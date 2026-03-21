<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="privacy-page">
    <section class="privacy-page__hero">
      <article class="privacy-page__hero-main">
        <p class="privacy-page__eyebrow">Privacy policy</p>
        <h1>
          Protect privacy,<br />
          <span>everywhere you work.</span>
        </h1>
        <p class="privacy-page__lead">
          SanitiseAI is designed as a privacy layer before text is shared with AI tools, docs, or internal workflows.
          This policy explains how processing works and what data is never stored.
        </p>
        <p class="privacy-page__effective">Effective date: March 21, 2026</p>
      </article>

      <aside class="privacy-page__principles" aria-label="Privacy principles">
        <h2>Privacy principles</h2>
        <ul>
          <li>
            <strong>No raw text storage</strong>
            <span>Submitted source text and sanitised output are not retained as user history.</span>
          </li>
          <li>
            <strong>Transient processing</strong>
            <span>Requests are processed in-memory for sanitisation and then discarded.</span>
          </li>
          <li>
            <strong>User control</strong>
            <span>You decide what to submit and what to share externally.</span>
          </li>
        </ul>
      </aside>
    </section>

    <section class="privacy-page__sections" aria-label="Policy sections">
      <article class="privacy-page__card">
        <h3>How text is processed</h3>
        <p>
          Submitted text is analysed to detect and replace sensitive entities. Processing is scoped to the active
          sanitisation request.
        </p>
      </article>

      <article class="privacy-page__card">
        <h3>What we do not store</h3>
        <ul>
          <li>Original text content.</li>
          <li>Sanitised output content.</li>
          <li>Detected entity values.</li>
        </ul>
      </article>

      <article class="privacy-page__card">
        <h3>Operational telemetry</h3>
        <p>
          We retain aggregate service metrics such as request counts, latency, and error rates. Raw request bodies are
          not intentionally logged.
        </p>
      </article>

      <article class="privacy-page__card">
        <h3>Rate limiting and abuse prevention</h3>
        <p>
          Free-tier limits may use a salted hashed key derived from request metadata. Raw IP addresses are not stored
          as user identity records.
        </p>
      </article>

      <article class="privacy-page__card">
        <h3>Payments and third-party processors</h3>
        <p>
          Payment checkout is handled by Stripe under Stripe's policies. SanitiseAI does not store full payment card
          details.
        </p>
      </article>

      <article class="privacy-page__card">
        <h3>Your controls</h3>
        <p>
          Review sanitised output before sharing with third-party systems. You are responsible for final content
          decisions after anonymisation.
        </p>
      </article>
    </section>

    <p class="privacy-page__notice">
      Privacy questions: contact via
      <a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer"
        >github.com/nimaparsi/matrix-anonymiser</a
      >
      or <a href="mailto:nimaparsi@icloud.com">nimaparsi@icloud.com</a>.
    </p>

    <section class="privacy-page__cta" aria-label="Final call to action">
      <h2>Ready to secure your workflow?</h2>
      <p>Use SanitiseAI now to remove sensitive entities before sharing text externally.</p>
      <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Open sanitiser</RouterLink>
    </section>
  </main>
</template>

<style scoped lang="scss">
.privacy-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2rem;

  &__hero {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 0.9rem;
  }

  &__hero-main,
  &__principles {
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 20%);
    border-radius: 16px;
    box-shadow: var(--shadow-sm);
    padding: clamp(1.2rem, 3vw, 1.8rem);
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-1);
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 760;
  }

  h1 {
    margin: 0.8rem 0 0;
    font-family: Manrope, Inter, sans-serif;
    font-size: clamp(2rem, 5vw, 3.8rem);
    line-height: 0.94;
    letter-spacing: -0.05em;

    span {
      color: var(--accent-1);
    }
  }

  &__lead {
    margin: 1rem 0 0;
    max-width: 60ch;
    color: var(--text-2);
    font-size: 1rem;
    line-height: 1.68;
  }

  &__effective {
    margin: 0.82rem 0 0;
    color: var(--text-3);
    font-size: 0.76rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 740;
  }

  &__principles {
    h2 {
      margin: 0;
      font-size: 1rem;
      letter-spacing: -0.01em;
    }

    ul {
      margin: 0.8rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.5rem;
    }

    li {
      border-radius: 10px;
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 44%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
      padding: 0.64rem 0.72rem;
      color: var(--text-2);
      font-size: 0.88rem;
      line-height: 1.45;
      display: grid;
      gap: 0.2rem;
    }

    strong {
      display: block;
      color: var(--text-1);
      font-size: 0.76rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 0.1rem;
    }
  }

  &__sections {
    margin-top: 1rem;
    display: grid;
    gap: 0.8rem;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  &__card {
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 26%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
    box-shadow: var(--shadow-sm);
    padding: 1rem;

    h3 {
      margin: 0;
      font-size: 1rem;
      letter-spacing: -0.015em;
    }

    p {
      margin: 0.58rem 0 0;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.66;
    }

    ul {
      margin: 0.6rem 0 0;
      padding-left: 1rem;
    }

    li {
      margin: 0.34rem 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.5;
    }

    li::marker {
      color: var(--ok);
    }
  }

  &__notice {
    margin-top: 1rem;
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 78%);
    background: color-mix(in srgb, var(--accent-soft), white 34%);
    color: var(--accent-1);
    padding: 0.86rem 1rem;
    font-size: 0.88rem;
    line-height: 1.55;
    font-weight: 650;

    a {
      color: inherit;
      text-decoration: underline;
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }
  }

  &__cta {
    margin-top: 1.2rem;
    border-radius: 18px;
    background: linear-gradient(180deg, #406ff7, #2f62f5);
    color: #fff;
    text-align: center;
    padding: clamp(1.8rem, 4vw, 2.8rem);
    box-shadow: var(--shadow-md);

    h2 {
      margin: 0;
      font-size: clamp(1.8rem, 4vw, 2.7rem);
      line-height: 1.02;
      letter-spacing: -0.04em;
      color: #fff;
    }

    p {
      margin: 0.84rem auto 0;
      max-width: 54ch;
      color: color-mix(in srgb, #fff, transparent 16%);
      font-size: 0.95rem;
      line-height: 1.6;
    }

    .btn {
      margin-top: 1rem;
      background: #fff;
      color: var(--accent-3);
      border-color: color-mix(in srgb, #fff, transparent 50%);
      box-shadow: none;
    }
  }
}

@media (max-width: 1000px) {
  .privacy-page {
    width: min(1200px, calc(100% - 1rem));

    &__hero {
      grid-template-columns: 1fr;
    }

    &__sections {
      grid-template-columns: 1fr;
    }
  }
}
</style>
