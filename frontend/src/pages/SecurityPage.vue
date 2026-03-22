<script setup lang="ts">
import { RouterLink } from 'vue-router'
import {
  PhArrowRight,
  PhCheckCircle,
  PhCloudArrowDown,
  PhDetective,
  PhFingerprint,
  PhLockKeyOpen,
  PhShieldCheck,
  PhStackSimple,
} from '@phosphor-icons/vue'

const standards = [
  { label: 'In-memory processing', icon: PhStackSimple },
  { label: 'No raw text storage', icon: PhShieldCheck },
  { label: 'Encrypted transport', icon: PhLockKeyOpen },
  { label: 'Dependency scanning', icon: PhFingerprint },
]

const showcaseCards = [
  {
    title: 'Edge sanitization',
    body: 'Sensitive text is sanitised before downstream sharing so unredacted values are masked as early as possible.',
    icon: PhCloudArrowDown,
  },
  {
    title: 'Immutable change controls',
    body: 'Operational changes follow controlled releases with traceable review history and rollback coverage.',
    icon: PhFingerprint,
  },
  {
    title: 'Layered detection',
    body: 'Entity detection and deterministic pattern matching run together to improve practical output quality.',
    icon: PhDetective,
  },
]

const lifecycle = [
  {
    step: '01. Ingestion',
    title: 'Secure inbound',
    body: 'Input is received over encrypted transport and handled in active processing memory.',
  },
  {
    step: '02. Sanitisation',
    title: 'PII detection',
    body: 'Entity and pattern detectors identify names, contact data, identifiers, and common secret formats.',
  },
  {
    step: '03. Anonymization',
    title: 'Token replacement',
    body: 'Detected values are replaced with structured placeholders to preserve context for safe sharing.',
  },
  {
    step: '04. Delivery',
    title: 'Clean output',
    body: 'Sanitised text is returned and transient request buffers are released at the end of the request lifecycle.',
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
          Security is foundational to SanitiseAI. The product is built as a local-first privacy layer that helps teams
          sanitise sensitive text before sharing it with AI tools, docs, or workflows.
        </p>

        <div class="security-page__hero-actions">
          <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
            <span>View Trust Report</span>
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
          <RouterLink class="btn btn--secondary" to="/privacy">Technical Docs</RouterLink>
        </div>
      </div>

      <article class="security-page__hero-visual" aria-label="Security overview visual">
        <img
          class="security-page__hero-image"
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuAMeznbs1t1VLCIDOwrFxjr3qDf8Ho5Tb2Z9P5tV4KVIBRxQF6T4hDTehZtnNUefWg0pDqZX72Ct-ruG-U3kbf5AWIeGNfWwmhQNRSomvOi8BriRsesR6KiWgEjhNmwtjehwEPn29wy-pkzPj3GUDqcGAuootZdgFbxk3FT3bVUgFXhGQoM4H7tlW_-VD4VAn9n6wFud8BOk0KZYWtM3xfA7byCw0XkYVKAiyDgdQifb3-2HaW7r0a81Bd5M8ITolKKLGzK5VHRupc"
          alt="Abstract blue security visualization"
        />

        <aside class="security-page__status-card">
          <p>
            <PhCheckCircle :size="13" weight="fill" aria-hidden="true" />
            Anonymization status
          </p>
          <strong>99.9%</strong>
          <div class="security-page__status-line"><span></span></div>
          <small>Reliability methodology v4.2</small>
        </aside>
      </article>
    </section>

    <section class="security-page__standards">
      <p>Operational safeguards</p>
      <ul>
        <li v-for="item in standards" :key="item.label">
          <component :is="item.icon" :size="15" weight="duotone" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </li>
      </ul>
    </section>

    <section class="security-page__showcase">
      <header>
        <h2>Zero-Trust Technical Showcase</h2>
        <p>Architecture controls focus on reducing exposure at ingest, processing, and delivery.</p>
      </header>

      <div class="security-page__showcase-grid">
        <article class="security-page__card security-page__card--large">
          <small>Foundational architecture</small>
          <h3>Deterministic + entity-aware pipeline</h3>
          <p>
            SanitiseAI combines deterministic pattern matching with entity-aware analysis to produce practical,
            readable anonymised output for contracts, notes, support logs, and prompt drafts.
          </p>
          <div class="security-page__large-metrics">
            <div>
              <span>Pattern scanning</span>
              <strong>Enabled</strong>
            </div>
            <div>
              <span>Entity detection</span>
              <strong>Enabled</strong>
            </div>
          </div>
        </article>

        <article class="security-page__card security-page__card--accent">
          <PhLockKeyOpen :size="24" weight="duotone" aria-hidden="true" />
          <h3>Transport security</h3>
          <p>Requests run over encrypted transport and sanitized output is returned through the same protected path.</p>
          <small>Security controls</small>
        </article>

        <article v-for="card in showcaseCards" :key="card.title" class="security-page__card security-page__card--small">
          <span class="security-page__icon">
            <component :is="card.icon" :size="16" weight="duotone" aria-hidden="true" />
          </span>
          <h4>{{ card.title }}</h4>
          <p>{{ card.body }}</p>
        </article>
      </div>
    </section>

    <section class="security-page__lifecycle">
      <div class="security-page__lifecycle-head">
        <div>
          <h2>Transparent Data Lifecycle</h2>
          <p>Understand how text moves through SanitiseAI from raw input to share-ready output.</p>
        </div>
        <div class="security-page__lifecycle-pills">
          <span>Live data status</span>
          <span>Encrypted</span>
        </div>
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
      <p>Review implementation notes, then run SanitiseAI with your own real content in the tool.</p>
      <div>
        <a class="btn btn--primary" href="mailto:nimaparsi@icloud.com">Talk to Compliance</a>
        <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Open Sanitiser</RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped lang="scss">
.security-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.2rem;
  padding-bottom: 1rem;

  &__hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(340px, 0.92fr);
    gap: 1.2rem;
    align-items: stretch;
  }

  &__hero-copy {
    h1 {
      margin: 0.7rem 0 0;
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(3rem, 6.4vw, 5.1rem);
      line-height: 0.92;
      letter-spacing: -0.055em;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 0.95rem 0 0;
      max-width: 48ch;
      color: var(--text-2);
      font-size: 1rem;
      line-height: 1.62;
    }
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-1);
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 760;
  }

  &__hero-actions {
    margin-top: 1.15rem;
    display: inline-flex;
    align-items: center;
    gap: 0.56rem;
    flex-wrap: wrap;

    .btn {
      min-height: 48px;
      padding-inline: 1rem;
    }
  }

  &__hero-visual {
    position: relative;
    border-radius: 16px;
    min-height: 420px;
    overflow: visible;
  }

  &__hero-image {
    width: 100%;
    height: 100%;
    min-height: 420px;
    object-fit: cover;
    border-radius: 16px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    box-shadow: 0 24px 46px rgba(0, 73, 219, 0.1);
    display: block;
  }

  &__status-card {
    position: absolute;
    left: -0.95rem;
    bottom: -0.95rem;
    z-index: 2;
    border-radius: 12px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 10%);
    background: color-mix(in srgb, var(--surface-0), white 2%);
    box-shadow: 0 22px 40px rgba(12, 21, 38, 0.16);
    padding: 0.8rem 0.9rem;
    width: min(280px, calc(100% - 1rem));

    p {
      margin: 0;
      display: inline-flex;
      align-items: center;
      gap: 0.34rem;
      font-size: 0.56rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-2);
      font-weight: 770;

      svg {
        color: var(--accent-1);
      }
    }

    strong {
      display: block;
      margin-top: 0.3rem;
      color: var(--accent-1);
      font-size: 1.75rem;
      letter-spacing: -0.03em;
      line-height: 1.03;
      font-family: Manrope, Inter, sans-serif;
    }

    .security-page__status-line {
      margin-top: 0.38rem;
      width: 100%;
      height: 4px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent-1), transparent 82%);
      overflow: hidden;

      span {
        display: block;
        width: 92%;
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #2962ff, #2457f5);
      }
    }

    small {
      display: block;
      margin-top: 0.35rem;
      color: var(--text-3);
      font-size: 0.56rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 720;
    }
  }

  &__standards {
    margin-top: 1.85rem;
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-2) 58%);
    padding: 1.3rem 1rem;

    p {
      margin: 0;
      text-align: center;
      color: var(--text-3);
      font-size: 0.58rem;
      letter-spacing: 0.19em;
      text-transform: uppercase;
      font-weight: 760;
    }

    ul {
      margin: 0.82rem auto 0;
      padding: 0;
      list-style: none;
      max-width: 980px;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.56rem;

      li {
        border-radius: 10px;
        min-height: 80px;
        padding: 0.62rem;
        display: grid;
        justify-items: center;
        align-content: center;
        gap: 0.42rem;
        text-align: center;
        background: color-mix(in srgb, var(--surface-0), var(--surface-1) 32%);
        border: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
        box-shadow: var(--shadow-xs);
        color: var(--text-2);

        svg {
          color: var(--accent-1);
        }

        span {
          font-size: 0.64rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          font-weight: 740;
        }
      }
    }
  }

  &__showcase {
    margin-top: 2.3rem;

    header {
      h2 {
        margin: 0;
        font-size: clamp(2rem, 4.4vw, 3.2rem);
        line-height: 1.05;
        letter-spacing: -0.045em;
      }

      p {
        margin: 0.58rem 0 0;
        max-width: 56ch;
        color: var(--text-2);
        font-size: 0.95rem;
        line-height: 1.56;
      }
    }
  }

  &__showcase-grid {
    margin-top: 0.95rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.64rem;
  }

  &__card {
    border-radius: 14px;
    padding: 1rem;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 26%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 20%);
    box-shadow: var(--shadow-xs);
  }

  &__card--large {
    grid-column: span 2;
    min-height: 218px;

    small {
      display: inline-flex;
      border-radius: 999px;
      padding: 0.24rem 0.52rem;
      background: color-mix(in srgb, var(--accent-soft), white 26%);
      color: var(--accent-3);
      font-size: 0.56rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 760;
    }

    h3 {
      margin: 0.68rem 0 0;
      font-size: 1.72rem;
      line-height: 1.08;
      letter-spacing: -0.035em;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0.56rem 0 0;
      max-width: 55ch;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.54;
    }
  }

  &__large-metrics {
    margin-top: 0.88rem;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem;

    div {
      border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
      padding-top: 0.5rem;
    }

    span {
      display: block;
      color: var(--text-3);
      font-size: 0.58rem;
      text-transform: uppercase;
      letter-spacing: 0.11em;
      font-weight: 760;
    }

    strong {
      display: block;
      margin-top: 0.24rem;
      color: var(--accent-1);
      font-size: 1.04rem;
      letter-spacing: -0.02em;
      font-weight: 760;
    }
  }

  &__card--accent {
    min-height: 218px;
    display: grid;
    align-content: start;
    gap: 0.52rem;
    background: linear-gradient(180deg, #2a60f6, #1349dd);
    color: white;
    border-color: color-mix(in srgb, #2457f5, transparent 22%);
    box-shadow: 0 20px 32px rgba(36, 87, 245, 0.24);

    svg {
      color: white;
    }

    h3 {
      margin: 0.14rem 0 0;
      color: white;
      font-size: 1.42rem;
      line-height: 1.1;
      letter-spacing: -0.03em;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0;
      color: color-mix(in srgb, white, transparent 12%);
      font-size: 0.86rem;
      line-height: 1.5;
    }

    small {
      margin-top: auto;
      font-size: 0.6rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: color-mix(in srgb, white, transparent 18%);
      font-weight: 760;
    }
  }

  &__card--small {
    min-height: 144px;

    h4 {
      margin: 0.6rem 0 0;
      font-size: 1.22rem;
      line-height: 1.1;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.46rem 0 0;
      color: var(--text-2);
      font-size: 0.8rem;
      line-height: 1.5;
    }
  }

  &__icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    color: var(--accent-1);
    background: color-mix(in srgb, var(--accent-soft), white 42%);
  }

  &__lifecycle {
    margin-top: 2.2rem;
  }

  &__lifecycle-head {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 1rem;

    h2 {
      margin: 0;
      font-size: clamp(1.95rem, 4.2vw, 3rem);
      line-height: 1.06;
      letter-spacing: -0.045em;
    }

    p {
      margin: 0.56rem 0 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.56;
      max-width: 56ch;
    }
  }

  &__lifecycle-pills {
    display: inline-flex;
    gap: 0.42rem;
    flex-shrink: 0;

    span {
      border-radius: 999px;
      padding: 0.24rem 0.54rem;
      background: color-mix(in srgb, var(--surface-2), white 16%);
      color: var(--text-3);
      font-size: 0.56rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 760;

      &:last-child {
        background: color-mix(in srgb, var(--accent-soft), white 16%);
        color: var(--accent-3);
      }
    }
  }

  &__lifecycle-grid {
    margin: 0.84rem 0 0;
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.62rem;

    li {
      border-radius: 12px;
      min-height: 178px;
      padding: 0.84rem;
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
      display: grid;
      align-content: start;
      gap: 0.46rem;

      &:last-child {
        background: linear-gradient(180deg, #2a60f6, #1349dd);
        border-color: color-mix(in srgb, #2457f5, transparent 22%);

        small,
        h4 {
          color: white;
        }

        p {
          color: color-mix(in srgb, white, transparent 12%);
        }
      }
    }

    small {
      color: var(--accent-1);
      font-size: 0.56rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 760;
    }

    h4 {
      margin: 0;
      font-size: 1.18rem;
      line-height: 1.08;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0;
      color: var(--text-2);
      font-size: 0.8rem;
      line-height: 1.48;
    }
  }

  &__cta {
    margin-top: 2.1rem;
    border-radius: 18px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 44%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    padding: clamp(1.2rem, 4vw, 1.9rem);
    text-align: center;

    h3 {
      margin: 0;
      font-size: clamp(2rem, 4.4vw, 3rem);
      line-height: 1.06;
      letter-spacing: -0.045em;
    }

    p {
      margin: 0.62rem auto 0;
      max-width: 56ch;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.56;
    }

    div {
      margin-top: 0.9rem;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 0.56rem;
    }
  }
}

@media (max-width: 1080px) {
  .security-page {
    width: min(1200px, calc(100% - 1rem));

    &__hero,
    &__showcase-grid,
    &__lifecycle-grid,
    &__standards ul {
      grid-template-columns: 1fr;
    }

    &__hero-visual {
      min-height: 360px;
    }

    &__hero-image {
      min-height: 360px;
    }

    &__status-card {
      min-width: 0;
      left: 0.8rem;
      right: 0.8rem;
      bottom: 0.8rem;
      width: auto;
    }

    &__lifecycle-head {
      flex-direction: column;
      align-items: flex-start;
    }
  }
}
</style>
