<script setup lang="ts">
import { RouterLink } from 'vue-router'
import {
  PhCheckCircle,
  PhCirclesFour,
  PhDetective,
  PhFingerprint,
  PhLockKeyOpen,
  PhShieldCheck,
  PhTarget,
} from '@phosphor-icons/vue'

const reliabilityCards = [
  {
    title: 'Entity Detection',
    body: 'Detects people, organisations, locations, and dates using layered detection strategies.',
    icon: PhDetective,
  },
  {
    title: 'Pattern Matching',
    body: 'Finds identifiers such as emails, phone numbers, URLs, IPs, and common secret-key formats.',
    icon: PhFingerprint,
  },
  {
    title: 'Contextual Analysis',
    body: 'Uses surrounding syntax cues to reduce false positives and improve practical output quality.',
    icon: PhTarget,
  },
]

const rights = [
  {
    title: 'Access',
    body: 'Request account-level metadata related to billing or support interactions.',
  },
  {
    title: 'Rectification',
    body: 'Correct inaccurate account contact details or support profile settings.',
  },
  {
    title: 'Erasure',
    body: 'Request deletion of account-linked records where legally and operationally permitted.',
  },
  {
    title: 'Portability',
    body: 'Request exports of account-linked records in standard machine-readable formats.',
  },
]
</script>

<template>
  <main class="privacy-page">
    <section class="privacy-page__hero">
      <div class="privacy-page__hero-copy">
        <p class="privacy-page__badge">
          <PhCheckCircle :size="12" weight="fill" aria-hidden="true" />
          Privacy by design
        </p>
        <h1>
          The Transparent<br />
          <span>Fortress.</span>
        </h1>
        <p>
          Security is foundational to SanitiseAI. Text is sanitised in a local-first flow designed to minimize data
          exposure before content is shared externally.
        </p>

        <div class="privacy-page__hero-pills">
          <span><PhCirclesFour :size="12" weight="duotone" aria-hidden="true" /> In-memory processing</span>
          <span><PhLockKeyOpen :size="12" weight="duotone" aria-hidden="true" /> Local-first flow</span>
        </div>
      </div>

      <aside class="privacy-page__shield-panel" aria-label="Security overview">
        <div class="privacy-page__shield-frame">
          <PhShieldCheck :size="110" weight="duotone" aria-hidden="true" />
        </div>
      </aside>
    </section>

    <section class="privacy-page__reliability">
      <header>
        <h2>How Sanitisation Works</h2>
        <p>Multiple detection layers are combined to identify sensitive entities before output is returned.</p>
      </header>

      <div class="privacy-page__reliability-grid">
        <article v-for="card in reliabilityCards" :key="card.title" class="privacy-page__card">
          <span class="privacy-page__card-icon">
            <component :is="card.icon" :size="16" weight="duotone" aria-hidden="true" />
          </span>
          <h3>{{ card.title }}</h3>
          <p>{{ card.body }}</p>
        </article>
      </div>
    </section>

    <section class="privacy-page__dark-band">
      <div class="privacy-page__dark-copy">
        <h3>The Data Lifecycle</h3>
        <p>
          Input is analysed, sanitised, and returned in a single request lifecycle. Raw payloads are not intended to be
          persisted as document history.
        </p>
        <ul>
          <li>
            <strong>In-memory request handling</strong>
            <span>Working text is processed in transient memory and released after response completion.</span>
          </li>
          <li>
            <strong>Minimal operational telemetry</strong>
            <span>Service health metrics focus on latency and errors rather than full payload retention.</span>
          </li>
        </ul>
      </div>

      <div class="privacy-page__flow">
        <div>Input</div>
        <span></span>
        <div>Processing</div>
        <span></span>
        <div>Output</div>
      </div>
    </section>

    <section class="privacy-page__governance">
      <div class="privacy-page__governance-art" aria-hidden="true">
        <div class="privacy-page__beam"></div>
      </div>

      <article class="privacy-page__governance-copy">
        <h3>Zero-Retention Governance</h3>
        <ol>
          <li>
            <strong>01</strong>
            <div>
              <h4>Instantaneous Purge</h4>
              <p>After sanitisation completes, transient request buffers are released from active processing memory.</p>
            </div>
          </li>
          <li>
            <strong>02</strong>
            <div>
              <h4>No document vault</h4>
              <p>SanitiseAI is designed as a pass-through privacy layer rather than a stored document workspace.</p>
            </div>
          </li>
        </ol>
      </article>
    </section>

    <section class="privacy-page__rights">
      <header>
        <h3>Your Data Controls</h3>
        <p>Privacy workflows include clear controls for account-linked records and support interactions.</p>
      </header>

      <div class="privacy-page__rights-grid">
        <article v-for="right in rights" :key="right.title">
          <small>Right to</small>
          <h4>{{ right.title }}</h4>
          <p>{{ right.body }}</p>
        </article>
      </div>
    </section>

    <section class="privacy-page__compliance">
      <div class="privacy-page__compliance-copy">
        <h3>Security Controls Overview</h3>
        <p>Current controls are focused on practical risk reduction in daily sanitisation workflows.</p>
      </div>
      <div class="privacy-page__compliance-badges">
        <span>TLS in transit</span>
        <span>Rate limiting</span>
        <span>Secrets management</span>
        <span>Dependency scanning</span>
      </div>
    </section>

    <section class="privacy-page__cta">
      <h3>Need security details for your team?</h3>
      <p>Contact support for implementation notes, then run SanitiseAI with your own real content.</p>
      <div>
        <RouterLink class="btn btn--secondary" :to="{ path: '/contact', query: { topic: 'support-request' } }">
          Contact support
        </RouterLink>
        <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">Open sanitiser</RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped lang="scss">
.privacy-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2rem;
  padding-bottom: 1rem;

  &__hero {
    display: grid;
    grid-template-columns: 1.12fr 0.88fr;
    gap: 1rem;
    align-items: stretch;
  }

  &__hero-copy {
    padding: 0.3rem 0.2rem;

    h1 {
      margin: 0.68rem 0 0;
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(2.8rem, 6vw, 4.6rem);
      line-height: 0.9;
      letter-spacing: -0.055em;

      span {
        color: var(--accent-1);
        font-style: italic;
      }
    }

    p {
      margin: 1rem 0 0;
      max-width: 48ch;
      color: var(--text-2);
      font-size: 1.02rem;
      line-height: 1.66;
    }
  }

  &__badge {
    margin: 0;
    display: inline-flex;
    align-items: center;
    gap: 0.36rem;
    border-radius: 999px;
    background: color-mix(in srgb, var(--accent-soft), white 40%);
    color: color-mix(in srgb, var(--accent-3), var(--accent-1) 30%);
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 76%);
    padding: 0.24rem 0.62rem;
    font-size: 0.58rem;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    font-weight: 780;
  }

  &__hero-pills {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.48rem;

    span {
      display: inline-flex;
      align-items: center;
      gap: 0.34rem;
      border-radius: 9px;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 16%);
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 40%);
      color: var(--text-2);
      font-size: 0.63rem;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      font-weight: 760;
      padding: 0.44rem 0.62rem;
    }
  }

  &__shield-panel {
    border-radius: 18px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 38%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 28%);
    padding: 0.95rem;
    display: grid;
    place-items: center;
    min-height: 320px;
  }

  &__shield-frame {
    width: min(360px, 100%);
    aspect-ratio: 1 / 1;
    border-radius: 12px;
    background: color-mix(in srgb, white, var(--surface-1) 46%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    display: grid;
    place-items: center;
    color: color-mix(in srgb, var(--accent-1), var(--accent-3) 26%);
    box-shadow: var(--shadow-sm);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      inset: -12px;
      border-radius: 16px;
      border: 2px dashed color-mix(in srgb, var(--accent-1), transparent 78%);
      pointer-events: none;
    }
  }

  &__reliability {
    margin-top: 2.4rem;
    padding-top: 2rem;
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);

    header {
      h2 {
        margin: 0;
        font-size: clamp(1.9rem, 4vw, 3rem);
        letter-spacing: -0.04em;
        line-height: 1.05;
      }

      p {
        margin: 0.62rem 0 0;
        max-width: 56ch;
        color: var(--text-2);
        font-size: 0.94rem;
        line-height: 1.58;
      }
    }
  }

  &__reliability-grid {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.8rem;
  }

  &__card {
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 35%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 22%);
    padding: 1rem;
    box-shadow: var(--shadow-xs);

    h3 {
      margin: 0.6rem 0 0;
      font-size: 1.18rem;
      letter-spacing: -0.02em;
      line-height: 1.12;
    }

    p {
      margin: 0.52rem 0 0;
      color: var(--text-2);
      font-size: 0.86rem;
      line-height: 1.55;
    }
  }

  &__card-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    color: var(--accent-1);
    background: color-mix(in srgb, var(--accent-soft), white 44%);
  }

  &__dark-band {
    margin-top: 1.7rem;
    border-radius: 20px;
    background: radial-gradient(circle at 20% 20%, #17224a, #071335 60%);
    color: white;
    padding: clamp(1.4rem, 4vw, 2.4rem);
    display: grid;
    grid-template-columns: 1fr 0.96fr;
    gap: 1rem;
    align-items: center;
  }

  &__dark-copy {
    h3 {
      margin: 0;
      color: white;
      font-size: clamp(1.6rem, 3vw, 2.4rem);
      letter-spacing: -0.03em;
      line-height: 1.05;
    }

    p {
      margin: 0.75rem 0 0;
      color: color-mix(in srgb, white, transparent 15%);
      font-size: 0.92rem;
      line-height: 1.62;
      max-width: 58ch;
    }

    ul {
      margin: 0.92rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.55rem;
    }

    li {
      display: grid;
      gap: 0.16rem;
    }

    strong {
      color: #a8e8c5;
      font-size: 0.8rem;
      letter-spacing: 0.02em;
    }

    span {
      color: color-mix(in srgb, white, transparent 25%);
      font-size: 0.8rem;
      line-height: 1.45;
    }
  }

  &__flow {
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, #7f99d8, transparent 58%);
    background: color-mix(in srgb, #090f2a, #152652 40%);
    padding: 1rem;
    display: grid;
    grid-template-columns: auto 1fr auto 1fr auto;
    align-items: center;
    gap: 0.5rem;

    div {
      border-radius: 10px;
      background: color-mix(in srgb, #2f5de6, #1a2b64 50%);
      color: #d7e6ff;
      padding: 0.5rem 0.65rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.62rem;
      font-weight: 770;
      text-align: center;
      white-space: nowrap;
    }

    span {
      display: block;
      height: 1px;
      background: linear-gradient(90deg, color-mix(in srgb, #aac6ff, transparent 10%), color-mix(in srgb, #aac6ff, transparent 70%));
    }
  }

  &__governance {
    margin-top: 1.7rem;
    display: grid;
    grid-template-columns: 0.86fr 1.14fr;
    gap: 1rem;
    align-items: stretch;
  }

  &__governance-art {
    border-radius: 14px;
    background: linear-gradient(180deg, #6c6c72, #4f5057);
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
  }

  &__beam {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 48%, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.03) 45%, transparent 70%);
    filter: blur(0.2px);
  }

  &__governance-copy {
    h3 {
      margin: 0;
      font-size: clamp(1.7rem, 4vw, 2.6rem);
      letter-spacing: -0.03em;
      line-height: 1.05;
    }

    ol {
      margin: 1rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.86rem;
    }

    li {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 0.62rem;
      align-items: start;
    }

    strong {
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent-soft), white 30%);
      color: var(--accent-1);
      display: grid;
      place-items: center;
      font-size: 0.62rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 760;
    }

    h4 {
      margin: 0;
      font-size: 1.04rem;
      letter-spacing: -0.015em;
      line-height: 1.2;
    }

    p {
      margin: 0.34rem 0 0;
      color: var(--text-2);
      font-size: 0.86rem;
      line-height: 1.54;
      max-width: 56ch;
    }
  }

  &__rights {
    margin-top: 2rem;

    header {
      text-align: center;

      h3 {
        margin: 0;
        font-size: clamp(1.8rem, 4vw, 2.8rem);
        letter-spacing: -0.035em;
        line-height: 1.04;
      }

      p {
        margin: 0.55rem 0 0;
        color: var(--text-2);
        font-size: 0.9rem;
      }
    }
  }

  &__rights-grid {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.7rem;

    article {
      border-radius: 12px;
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 28%);
      padding: 0.92rem;
      min-height: 176px;
      box-shadow: var(--shadow-xs);
    }

    small {
      color: var(--accent-1);
      font-size: 0.56rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-weight: 760;
    }

    h4 {
      margin: 0.5rem 0 0;
      font-size: 1.3rem;
      line-height: 1.08;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.54rem 0 0;
      color: var(--text-2);
      font-size: 0.82rem;
      line-height: 1.5;
    }
  }

  &__compliance {
    margin-top: 1.6rem;
    padding-top: 1.1rem;
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 26%);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 1rem;
    align-items: center;
  }

  &__compliance-copy {
    h3 {
      margin: 0;
      font-size: 1.25rem;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.44rem 0 0;
      color: var(--text-2);
      font-size: 0.84rem;
      line-height: 1.54;
    }
  }

  &__compliance-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: flex-end;

    span {
      border-radius: 9px;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 14%);
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 42%);
      color: var(--text-2);
      padding: 0.46rem 0.62rem;
      font-size: 0.64rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 760;
    }
  }

  &__cta {
    margin-top: 1.25rem;
    border-radius: 16px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 20%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 28%);
    padding: 1rem;
    display: grid;
    gap: 0.5rem;

    h3 {
      margin: 0;
      font-size: 1.24rem;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0;
      color: var(--text-2);
      font-size: 0.88rem;
      line-height: 1.52;
    }

    div {
      margin-top: 0.3rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
    }
  }
}

@media (max-width: 1080px) {
  .privacy-page {
    width: min(1200px, calc(100% - 1rem));

    &__hero,
    &__dark-band,
    &__governance,
    &__compliance {
      grid-template-columns: 1fr;
    }

    &__reliability-grid {
      grid-template-columns: 1fr;
    }

    &__rights-grid {
      grid-template-columns: 1fr 1fr;
    }

    &__compliance-badges {
      justify-content: flex-start;
    }
  }
}

@media (max-width: 700px) {
  .privacy-page {
    &__rights-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
