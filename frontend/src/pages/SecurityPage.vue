<script setup lang="ts">
import { RouterLink } from 'vue-router'
import {
  PhArrowRight,
  PhBracketsCurly,
  PhCheckCircle,
  PhCloud,
  PhCode,
  PhDetective,
  PhFingerprint,
  PhLockKey,
  PhShieldCheck,
} from '@phosphor-icons/vue'

const standards = ['In-memory processing', 'No raw text storage', 'TLS in transit', 'Dependency checks']

const capabilityCards = [
  {
    title: 'Edge sanitisation',
    body: 'Text is sanitised before sharing downstream, so sensitive values are masked at the earliest practical step.',
    icon: PhCloud,
  },
  {
    title: 'Configurable detectors',
    body: 'Teams can run automatic detection or custom detector profiles for names, secrets, network data, and identifiers.',
    icon: PhDetective,
  },
  {
    title: 'Minimal telemetry',
    body: 'Operational metrics focus on uptime and errors. Full raw payload capture is not used for routine operation.',
    icon: PhFingerprint,
  },
]

const lifecycle = [
  {
    step: '01. Ingestion',
    title: 'Secure input',
    body: 'Text is submitted over encrypted transport and held in transient processing memory.',
  },
  {
    step: '02. Sanitisation',
    title: 'PII detection',
    body: 'Entity and pattern detectors identify sensitive fields and select safe replacements.',
  },
  {
    step: '03. Anonymization',
    title: 'Token replacement',
    body: 'Sensitive values are replaced with structured tags that preserve context and readability.',
  },
  {
    step: '04. Delivery',
    title: 'Clean output',
    body: 'Anonymised output is returned to the client while transient processing buffers are released.',
  },
]
</script>

<template>
  <main class="security-page">
    <section class="security-page__hero">
      <div class="security-page__hero-copy">
        <p class="security-page__eyebrow">Privacy &amp; Compliance</p>
        <h1>
          The Transparent<br />
          <span>Fortress.</span>
        </h1>
        <p>
          Security in SanitiseAI is designed as a practical privacy layer. We combine strong technical safeguards with
          clear, readable workflows so sensitive text can be processed safely.
        </p>

        <div class="security-page__hero-actions">
          <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
            <span>View Trust Report</span>
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
          <RouterLink class="btn btn--secondary" to="/privacy">Technical Docs</RouterLink>
        </div>
      </div>

      <article class="security-page__hero-visual" aria-label="Security signal">
        <div class="security-page__visual-surface" aria-hidden="true"></div>

        <aside class="security-page__status">
          <p>
            <PhCheckCircle :size="13" weight="fill" aria-hidden="true" />
            Anonymization status
          </p>
          <strong>Stable</strong>
          <small>Regression suite active</small>
        </aside>
      </article>
    </section>

    <section class="security-page__standards">
      <p>Globally recognized controls</p>
      <ul>
        <li v-for="item in standards" :key="item">{{ item }}</li>
      </ul>
    </section>

    <section class="security-page__showcase">
      <header>
        <h2>Zero-Trust Technical Showcase</h2>
        <p>Our architecture is built to reduce sensitive data exposure at ingestion, processing, and delivery.</p>
      </header>

      <div class="security-page__showcase-grid">
        <article class="security-page__card security-page__card--large">
          <small>Foundational architecture</small>
          <h3>Layered detection engine</h3>
          <p>
            The sanitisation pipeline combines deterministic pattern matching with entity-aware detection for stronger,
            practical redaction quality.
          </p>
          <dl>
            <div>
              <dt>Entity detection</dt>
              <dd>Enabled</dd>
            </div>
            <div>
              <dt>Pattern scanning</dt>
              <dd>Enabled</dd>
            </div>
          </dl>
        </article>

        <article class="security-page__card security-page__card--accent">
          <PhLockKey :size="22" weight="duotone" aria-hidden="true" />
          <h3>Transport security</h3>
          <p>Requests are protected in transit using HTTPS/TLS, with secure delivery of sanitised output.</p>
          <small>Security specs</small>
        </article>
      </div>

      <div class="security-page__capability-grid">
        <article v-for="card in capabilityCards" :key="card.title" class="security-page__card">
          <span class="security-page__icon">
            <component :is="card.icon" :size="16" weight="duotone" aria-hidden="true" />
          </span>
          <h4>{{ card.title }}</h4>
          <p>{{ card.body }}</p>
        </article>
      </div>
    </section>

    <section class="security-page__lifecycle">
      <header>
        <h2>Transparent Data Lifecycle</h2>
        <p>Understand how content flows through SanitiseAI from raw input to clean, share-ready output.</p>
      </header>

      <div class="security-page__lifecycle-meta">
        <span>Live data status</span>
        <span>Encrypted</span>
      </div>

      <ol class="security-page__lifecycle-grid">
        <li v-for="item in lifecycle" :key="item.step">
          <small>{{ item.step }}</small>
          <h4>{{ item.title }}</h4>
          <p>{{ item.body }}</p>
        </li>
      </ol>
    </section>

    <section class="security-page__cta">
      <h3>Ready to fortify your data?</h3>
      <p>Download security notes or run the sanitiser directly with production-like text samples.</p>
      <div>
        <a class="btn btn--primary" href="mailto:nimaparsi@icloud.com">Talk to Compliance</a>
        <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Open Sanitiser</RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped lang="scss">
.security-page {
  width: min(1220px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.2rem;
  padding-bottom: 1.2rem;

  &__hero {
    display: grid;
    grid-template-columns: 1fr 0.98fr;
    gap: 1.25rem;
    align-items: stretch;
  }

  &__hero-copy {
    h1 {
      margin: 0.72rem 0 0;
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(3rem, 6.2vw, 5rem);
      line-height: 0.92;
      letter-spacing: -0.052em;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 1rem 0 0;
      max-width: 48ch;
      color: var(--text-2);
      font-size: 1.02rem;
      line-height: 1.62;
    }
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-1);
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 780;
  }

  &__hero-actions {
    margin-top: 1.2rem;
    display: inline-flex;
    align-items: center;
    gap: 0.58rem;
    flex-wrap: wrap;

    .btn {
      min-height: 48px;
      padding-inline: 1rem;
    }
  }

  &__hero-visual {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    min-height: 420px;
    background: #051129;
    box-shadow: var(--shadow-sm);
  }

  &__visual-surface {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 78% 22%, rgba(66, 161, 255, 0.24), transparent 30%),
      radial-gradient(circle at 12% 72%, rgba(30, 144, 255, 0.16), transparent 36%),
      linear-gradient(180deg, #06142d 0%, #041027 50%, #030d23 100%);

    &::before {
      content: '';
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 20% 45%, rgba(73, 175, 255, 0.4) 2px, transparent 3px),
        radial-gradient(circle at 40% 38%, rgba(73, 175, 255, 0.24) 2px, transparent 3px),
        radial-gradient(circle at 66% 30%, rgba(73, 175, 255, 0.25) 2px, transparent 3px),
        radial-gradient(circle at 84% 40%, rgba(73, 175, 255, 0.3) 3px, transparent 4px),
        repeating-linear-gradient(
          170deg,
          transparent 0 14px,
          rgba(49, 138, 235, 0.1) 14px 15px,
          transparent 15px 22px
        );
      opacity: 0.86;
    }
  }

  &__status {
    position: absolute;
    left: 1.1rem;
    bottom: 1rem;
    z-index: 2;
    border-radius: 10px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
    box-shadow: var(--shadow-xs);
    padding: 0.72rem 0.78rem;
    min-width: 220px;

    p {
      margin: 0;
      display: inline-flex;
      align-items: center;
      gap: 0.34rem;
      font-size: 0.62rem;
      letter-spacing: 0.11em;
      text-transform: uppercase;
      color: var(--text-2);
      font-weight: 760;

      svg {
        color: var(--accent-1);
      }
    }

    strong {
      margin-top: 0.34rem;
      display: block;
      color: var(--accent-1);
      font-size: 1.8rem;
      letter-spacing: -0.03em;
      line-height: 1;
      font-family: Manrope, Inter, sans-serif;
    }

    small {
      margin-top: 0.18rem;
      display: block;
      color: var(--text-3);
      font-size: 0.62rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 730;
    }
  }

  &__standards {
    margin-top: 1.8rem;
    padding: 1.5rem 1rem;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 40%);
    border-radius: 14px;

    p {
      margin: 0;
      text-align: center;
      color: var(--text-3);
      font-size: 0.58rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      font-weight: 780;
    }

    ul {
      margin: 0.9rem auto 0;
      padding: 0;
      list-style: none;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.6rem;
      max-width: 820px;

      li {
        border-radius: 10px;
        background: color-mix(in srgb, var(--surface-0), var(--surface-1) 18%);
        min-height: 68px;
        display: grid;
        place-items: center;
        text-align: center;
        color: var(--text-2);
        font-size: 0.66rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 760;
      }
    }
  }

  &__showcase {
    margin-top: 2.4rem;

    header {
      h2 {
        margin: 0;
        font-size: clamp(1.95rem, 4.2vw, 3rem);
        line-height: 1.05;
        letter-spacing: -0.04em;
      }

      p {
        margin: 0.62rem 0 0;
        color: var(--text-2);
        max-width: 56ch;
        font-size: 0.95rem;
        line-height: 1.6;
      }
    }
  }

  &__showcase-grid {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 0.7rem;
  }

  &__card {
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    padding: 0.95rem;
  }

  &__card--large {
    min-height: 210px;

    small {
      display: inline-flex;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent-soft), white 22%);
      color: var(--accent-3);
      padding: 0.22rem 0.52rem;
      font-size: 0.56rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 760;
    }

    h3 {
      margin: 0.72rem 0 0;
      font-size: 2rem;
      line-height: 1.05;
      letter-spacing: -0.03em;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0.62rem 0 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.58;
      max-width: 52ch;
    }

    dl {
      margin: 1rem 0 0;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.5rem;

      div {
        border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 26%);
        padding-top: 0.55rem;
      }

      dt {
        color: var(--text-3);
        font-size: 0.58rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 760;
      }

      dd {
        margin: 0.28rem 0 0;
        color: var(--accent-1);
        font-size: 1.08rem;
        letter-spacing: -0.02em;
        font-weight: 780;
      }
    }
  }

  &__card--accent {
    background: linear-gradient(180deg, #2457f5, #1347d8);
    color: white;
    min-height: 210px;
    display: grid;
    align-content: start;
    gap: 0.56rem;

    svg {
      color: white;
    }

    h3 {
      margin: 0.2rem 0 0;
      color: white;
      font-size: 1.88rem;
      line-height: 1.05;
      letter-spacing: -0.03em;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0;
      color: color-mix(in srgb, white, transparent 10%);
      font-size: 0.86rem;
      line-height: 1.54;
    }

    small {
      margin-top: auto;
      color: color-mix(in srgb, white, transparent 16%);
      font-size: 0.6rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 760;
    }
  }

  &__capability-grid {
    margin-top: 0.72rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.7rem;

    .security-page__card {
      min-height: 134px;

      h4 {
        margin: 0.6rem 0 0;
        font-size: 1.36rem;
        line-height: 1.08;
        letter-spacing: -0.02em;
      }

      p {
        margin: 0.5rem 0 0;
        color: var(--text-2);
        font-size: 0.82rem;
        line-height: 1.52;
      }
    }
  }

  &__icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    color: var(--accent-1);
    background: color-mix(in srgb, var(--accent-soft), white 40%);
  }

  &__lifecycle {
    margin-top: 2.2rem;

    header {
      h2 {
        margin: 0;
        font-size: clamp(1.9rem, 4.1vw, 2.8rem);
        letter-spacing: -0.04em;
        line-height: 1.06;
      }

      p {
        margin: 0.56rem 0 0;
        max-width: 56ch;
        color: var(--text-2);
        font-size: 0.9rem;
        line-height: 1.56;
      }
    }
  }

  &__lifecycle-meta {
    margin-top: 0.62rem;
    display: inline-flex;
    gap: 0.4rem;

    span {
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-2), white 14%);
      color: var(--text-3);
      font-size: 0.56rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 760;
      padding: 0.24rem 0.52rem;

      &:last-child {
        background: color-mix(in srgb, var(--accent-soft), white 16%);
        color: var(--accent-3);
      }
    }
  }

  &__lifecycle-grid {
    margin: 0.85rem 0 0;
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.62rem;

    li {
      border-radius: 10px;
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 28%);
      min-height: 180px;
      padding: 0.82rem;
      display: grid;
      align-content: start;
      gap: 0.46rem;
    }

    small {
      color: var(--accent-1);
      font-size: 0.55rem;
      text-transform: uppercase;
      letter-spacing: 0.11em;
      font-weight: 760;
    }

    h4 {
      margin: 0;
      font-size: 1.2rem;
      line-height: 1.1;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0;
      color: var(--text-2);
      font-size: 0.78rem;
      line-height: 1.5;
    }
  }

  &__cta {
    margin-top: 2rem;
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 42%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    padding: clamp(1.2rem, 4vw, 1.8rem);
    text-align: center;

    h3 {
      margin: 0;
      font-size: clamp(1.9rem, 4.2vw, 3rem);
      letter-spacing: -0.04em;
      line-height: 1.05;
    }

    p {
      margin: 0.7rem auto 0;
      max-width: 56ch;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.58;
    }

    div {
      margin-top: 0.92rem;
      display: inline-flex;
      align-items: center;
      gap: 0.56rem;
      flex-wrap: wrap;
      justify-content: center;
    }
  }
}

@media (max-width: 1080px) {
  .security-page {
    width: min(1220px, calc(100% - 1rem));

    &__hero,
    &__showcase-grid,
    &__capability-grid,
    &__lifecycle-grid,
    &__standards ul {
      grid-template-columns: 1fr;
    }

    &__hero-visual {
      min-height: 320px;
    }

    &__status {
      min-width: 0;
      width: calc(100% - 2rem);
    }
  }
}
</style>
