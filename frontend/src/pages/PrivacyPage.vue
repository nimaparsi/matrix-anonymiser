<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhCheckCircle, PhDetective, PhFingerprint, PhLock, PhShieldCheck, PhTarget } from '@phosphor-icons/vue'

const reliabilityCards = [
  {
    title: 'Multi-layered masking',
    body: 'Regex, pattern heuristics, and entity-based detection are combined to reduce sensitive value leakage.',
    points: ['Adaptive tokenization', 'Format-preserving substitution'],
    icon: PhShieldCheck,
  },
  {
    title: 'Neural NER engine',
    body: 'Named-entity models improve identification in unstructured notes, contracts, and support transcripts.',
    points: ['Contextual disambiguation', 'Entity relationship checks'],
    icon: PhDetective,
  },
  {
    title: 'Semantic validation',
    body: 'Final verification checks reduce false positives and improve consistency in anonymised output.',
    points: ['Structural integrity checks', 'Automated remediation'],
    icon: PhTarget,
  },
]

const lifecycle = [
  {
    title: 'Data ingestion',
    body: 'Input arrives through encrypted transport and is handled in active request memory.',
    icon: PhFingerprint,
  },
  {
    title: 'In-memory masking',
    body: 'Detection and anonymisation run in transient processing scope without creating a document vault.',
    icon: PhShieldCheck,
  },
  {
    title: 'Secure output',
    body: 'Structured placeholders are returned so content remains useful while sensitive data stays protected.',
    icon: PhLock,
  },
  {
    title: 'Instant destruction',
    body: 'Temporary buffers are released after request completion as part of the normal processing lifecycle.',
    icon: PhCheckCircle,
  },
]

const compliance = ['SOC 2 Type II controls', 'GDPR alignment', 'HIPAA safeguards', 'ISO 27001 controls']

const rights = [
  {
    title: 'Access',
    body: 'Request account-linked support and billing metadata associated with your workspace usage.',
  },
  {
    title: 'Rectification',
    body: 'Update account and organisation profile details used for contact and support routing.',
  },
  {
    title: 'Erasure',
    body: 'Request deletion of account-linked records where operational and legal retention allows.',
  },
  {
    title: 'Portability',
    body: 'Request account-linked records in standard machine-readable formats when applicable.',
  },
]
</script>

<template>
  <main class="privacy-page">
    <section class="privacy-page__hero">
      <div class="privacy-page__hero-copy">
        <p class="privacy-page__eyebrow">
          <PhCheckCircle :size="12" weight="fill" aria-hidden="true" />
          Zero-trust architecture
        </p>

        <h1>
          Privacy &amp;<br />
          <span>Compliance</span>
        </h1>

        <p>
          SanitiseAI processes sensitive text in a local-first flow designed to minimize retention risk. Content is
          sanitised during request handling and returned as safe-to-share structured output.
        </p>

        <div class="privacy-page__hero-actions">
          <RouterLink class="btn btn--primary" :to="{ path: '/contact', query: { topic: 'security-review' } }">
            <span>Request security brief</span>
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
          <RouterLink class="btn btn--secondary" to="/security">View security page</RouterLink>
        </div>
      </div>

      <aside class="privacy-page__hero-media" aria-label="Privacy infrastructure visual">
        <div class="privacy-page__hero-frame">
          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDcNlcUNQKUomzqPzuOHZ-6E-AlYjaXM4X15s_k-7cvBR3rLJiv0BF86PDkLnpZRBhA7nsNgXmEWIlR8wX3-G7Zsroyjl97Hp1vYdHTMhSsx-Ytie2ZUDr-HmxshIxxyM1vhWkqO38PsYcD_Dns5CZWs3TzlAVi3OjbhTMtz45rUi1aW2gmV4UZL4wDTYckuyrgaFrerWsaunHxlGf11nfZubR3xoSD2mcK1Ip2GfYLNzF1tLWnXG8QyLMq6BVbpo0WTCVXG35IGNo"
            alt="Security infrastructure"
          />
        </div>
        <article class="privacy-page__status-card">
          <strong>
            <PhCheckCircle :size="14" weight="fill" aria-hidden="true" />
            100% Stateless
          </strong>
          <p>Transient processing memory is released after request completion.</p>
        </article>
      </aside>
    </section>

    <section class="privacy-page__reliability">
      <header>
        <p>Core technology</p>
        <h2>99.9% Reliability Methodology</h2>
      </header>

      <div class="privacy-page__reliability-grid">
        <article v-for="card in reliabilityCards" :key="card.title" class="privacy-page__reliability-card">
          <span class="privacy-page__card-icon">
            <component :is="card.icon" :size="18" weight="duotone" aria-hidden="true" />
          </span>
          <h3>{{ card.title }}</h3>
          <p>{{ card.body }}</p>
          <ul>
            <li v-for="point in card.points" :key="point">
              <PhCheckCircle :size="12" weight="fill" aria-hidden="true" />
              <span>{{ point }}</span>
            </li>
          </ul>
        </article>
      </div>
    </section>

    <section class="privacy-page__lifecycle">
      <header>
        <h2>Secure Data Lifecycle</h2>
        <p>From ingestion to cleanup, privacy controls are applied across the full request lifecycle.</p>
      </header>

      <ol class="privacy-page__lifecycle-grid">
        <li v-for="step in lifecycle" :key="step.title">
          <span class="privacy-page__step-icon">
            <component :is="step.icon" :size="15" weight="duotone" aria-hidden="true" />
          </span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.body }}</p>
        </li>
      </ol>
    </section>

    <section class="privacy-page__compliance-band">
      <div class="privacy-page__compliance-copy">
        <h2>Compliance-ready Controls</h2>
        <p>
          SanitiseAI is engineered to support common privacy and security frameworks through practical controls and
          auditable operational safeguards.
        </p>
        <div class="privacy-page__compliance-pills">
          <span>AES-256 transport</span>
          <span>Rate limiting</span>
          <span>Dependency scanning</span>
        </div>
      </div>

      <ul class="privacy-page__compliance-grid">
        <li v-for="item in compliance" :key="item">{{ item }}</li>
      </ul>
    </section>

    <section class="privacy-page__rights">
      <header>
        <h2>Your Rights (GDPR &amp; CCPA)</h2>
        <RouterLink class="privacy-page__rights-link" :to="{ path: '/contact', query: { topic: 'support-request' } }">
          Request privacy assistance
          <PhArrowRight :size="13" weight="bold" aria-hidden="true" />
        </RouterLink>
      </header>

      <div class="privacy-page__rights-grid">
        <article v-for="right in rights" :key="right.title">
          <h3>{{ right.title }}</h3>
          <p>{{ right.body }}</p>
        </article>
      </div>
    </section>

    <section class="privacy-page__cta">
      <h2>Ready to secure your data pipeline?</h2>
      <p>Run SanitiseAI on real content, then contact us for implementation and policy guidance.</p>
      <div>
        <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Start Free Trial</RouterLink>
        <RouterLink class="btn btn--primary" :to="{ path: '/contact', query: { topic: 'security-review' } }">
          Talk to Security Experts
        </RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped lang="scss">
.privacy-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.1rem;
  padding-bottom: 0.8rem;

  &__hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(320px, 0.95fr);
    gap: 1.1rem;
    align-items: center;
  }

  &__hero-copy {
    h1 {
      margin: 0.62rem 0 0;
      font-size: clamp(2.9rem, 6vw, 5.1rem);
      line-height: 0.92;
      letter-spacing: -0.055em;
      font-family: Manrope, Inter, sans-serif;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 0.98rem 0 0;
      max-width: 49ch;
      color: var(--text-2);
      font-size: 1.02rem;
      line-height: 1.65;
    }
  }

  &__eyebrow {
    margin: 0;
    display: inline-flex;
    align-items: center;
    gap: 0.33rem;
    border-radius: 999px;
    padding: 0.28rem 0.72rem;
    background: color-mix(in srgb, var(--accent-soft), white 36%);
    color: color-mix(in srgb, var(--accent-3), var(--accent-1) 30%);
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 76%);
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 780;
  }

  &__hero-actions {
    margin-top: 1.2rem;
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.58rem;

    .btn {
      min-height: 48px;
      padding-inline: 1rem;
    }
  }

  &__hero-media {
    position: relative;
    border-radius: 20px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 34%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    box-shadow: var(--shadow-sm);
    padding: 0.86rem;
  }

  &__hero-frame {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
    background: #0f172a;

    img {
      display: block;
      width: 100%;
      height: 290px;
      object-fit: cover;
    }
  }

  &__status-card {
    position: absolute;
    right: -0.2rem;
    bottom: -0.6rem;
    width: min(230px, calc(100% - 2rem));
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), transparent 18%);
    backdrop-filter: blur(14px) saturate(122%);
    -webkit-backdrop-filter: blur(14px) saturate(122%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 18%);
    box-shadow: var(--shadow-md);
    padding: 0.7rem;

    strong {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.78rem;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      color: var(--accent-3);
    }

    p {
      margin: 0.4rem 0 0;
      color: var(--text-2);
      font-size: 0.76rem;
      line-height: 1.45;
    }
  }

  &__reliability {
    margin-top: 2.8rem;

    header {
      p {
        margin: 0;
        color: var(--accent-1);
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.6rem;
        font-weight: 760;
      }

      h2 {
        margin: 0.56rem 0 0;
        font-size: clamp(2rem, 4vw, 3rem);
        letter-spacing: -0.04em;
        line-height: 1.03;
      }
    }
  }

  &__reliability-grid {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.8rem;
  }

  &__reliability-card {
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 42%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 22%);
    box-shadow: var(--shadow-xs);
    padding: 0.95rem;

    h3 {
      margin: 0.64rem 0 0;
      font-size: 1.28rem;
      letter-spacing: -0.03em;
      line-height: 1.1;
    }

    p {
      margin: 0.56rem 0 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.56;
    }

    ul {
      margin: 0.7rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.34rem;
    }

    li {
      display: inline-flex;
      align-items: center;
      gap: 0.34rem;
      color: var(--text-2);
      font-size: 0.77rem;
      line-height: 1.4;
    }
  }

  &__card-icon {
    width: 40px;
    height: 40px;
    border-radius: 11px;
    display: grid;
    place-items: center;
    background: color-mix(in srgb, var(--accent-soft), white 34%);
    color: var(--accent-1);
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 78%);
  }

  &__lifecycle {
    margin-top: 2.8rem;
    border-radius: 18px;
    background: color-mix(in srgb, var(--surface-1), white 8%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 25%);
    padding: 1rem;

    header {
      text-align: center;

      h2 {
        margin: 0;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        letter-spacing: -0.035em;
      }

      p {
        margin: 0.5rem auto 0;
        max-width: 66ch;
        color: var(--text-2);
        font-size: 0.9rem;
        line-height: 1.6;
      }
    }
  }

  &__lifecycle-grid {
    margin: 1rem 0 0;
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.66rem;

    li {
      border-radius: 14px;
      background: var(--surface-0);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 20%);
      padding: 0.78rem;
      text-align: center;
    }

    h3 {
      margin: 0.54rem 0 0;
      font-size: 1rem;
      letter-spacing: -0.02em;
      line-height: 1.2;
    }

    p {
      margin: 0.4rem 0 0;
      color: var(--text-2);
      font-size: 0.77rem;
      line-height: 1.48;
    }
  }

  &__step-icon {
    width: 38px;
    height: 38px;
    border-radius: 999px;
    display: inline-grid;
    place-items: center;
    background: color-mix(in srgb, var(--accent-soft), white 30%);
    color: var(--accent-1);
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 78%);
  }

  &__compliance-band {
    margin-top: 2.8rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #0d1730 0%, #0a1230 54%, #08102b 100%);
    color: #eef4ff;
    border: 1px solid color-mix(in srgb, #a9c3ff, transparent 82%);
    padding: 1.05rem;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 1rem;
  }

  &__compliance-copy {
    h2 {
      margin: 0;
      color: #f5f8ff;
      font-size: clamp(1.8rem, 4vw, 2.5rem);
      letter-spacing: -0.03em;
      line-height: 1.05;
    }

    p {
      margin: 0.6rem 0 0;
      max-width: 60ch;
      color: color-mix(in srgb, #dbe7ff, #9cb6e8 30%);
      font-size: 0.92rem;
      line-height: 1.55;
    }
  }

  &__compliance-pills {
    margin-top: 0.68rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.44rem;

    span {
      border-radius: 999px;
      padding: 0.34rem 0.58rem;
      font-size: 0.62rem;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      font-weight: 760;
      color: #c7d8ff;
      border: 1px solid color-mix(in srgb, #a9c3ff, transparent 72%);
      background: color-mix(in srgb, #1b2f5f, #0f1f45 42%);
    }
  }

  &__compliance-grid {
    margin: 0;
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem;
    align-content: center;

    li {
      min-width: 152px;
      border-radius: 12px;
      border: 1px solid color-mix(in srgb, #a9c3ff, transparent 78%);
      background: color-mix(in srgb, #1a2b58, #12234f 55%);
      padding: 0.54rem 0.64rem;
      font-size: 0.66rem;
      letter-spacing: 0.11em;
      text-transform: uppercase;
      font-weight: 760;
      color: #dce8ff;
      text-align: center;
    }
  }

  &__rights {
    margin-top: 2.8rem;

    header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 1rem;

      h2 {
        margin: 0;
        font-size: clamp(1.9rem, 4vw, 2.8rem);
        letter-spacing: -0.04em;
        line-height: 1.05;
      }
    }
  }

  &__rights-link {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    color: var(--accent-1);
    font-size: 0.76rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 760;
  }

  &__rights-grid {
    margin-top: 0.8rem;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.54rem;

    article {
      border-radius: 14px;
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 45%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 20%);
      padding: 0.78rem;
    }

    h3 {
      margin: 0;
      font-size: 1.02rem;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.45rem 0 0;
      color: var(--text-2);
      font-size: 0.78rem;
      line-height: 1.48;
    }
  }

  &__cta {
    margin-top: 2.8rem;
    border-radius: 20px;
    background: linear-gradient(160deg, #2457f5 0%, #1f4edf 100%);
    border: 1px solid color-mix(in srgb, #2759f4, transparent 36%);
    color: #f4f8ff;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 18px 36px color-mix(in srgb, #2457f5, transparent 72%);

    h2 {
      margin: 0;
      color: #f8fbff;
      font-size: clamp(2rem, 4vw, 3.1rem);
      letter-spacing: -0.04em;
      line-height: 1.02;
    }

    p {
      margin: 0.68rem auto 0;
      max-width: 64ch;
      color: color-mix(in srgb, #e7efff, #afc6f3 22%);
      font-size: 0.95rem;
      line-height: 1.58;
    }

    div {
      margin-top: 1rem;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.56rem;
      flex-wrap: wrap;
    }

    .btn--secondary {
      --btn-bg: #f8fbff;
      --btn-color: #1f48cc;
      --btn-border: color-mix(in srgb, white, transparent 30%);
    }

    .btn--primary {
      --btn-bg: color-mix(in srgb, #2f67ff, #1642c2 44%);
      --btn-color: #f4f8ff;
      --btn-border: color-mix(in srgb, #2f67ff, transparent 22%);
      --btn-shadow: 0 12px 26px color-mix(in srgb, #2f67ff, transparent 68%);
    }
  }
}

@media (max-width: 1100px) {
  .privacy-page {
    &__hero,
    &__reliability-grid,
    &__lifecycle-grid,
    &__rights-grid {
      grid-template-columns: 1fr 1fr;
    }

    &__compliance-band {
      grid-template-columns: 1fr;
    }

    &__status-card {
      position: static;
      width: 100%;
      margin-top: 0.66rem;
    }
  }
}

@media (max-width: 760px) {
  .privacy-page {
    width: min(1200px, calc(100% - 1rem));

    &__hero,
    &__reliability-grid,
    &__lifecycle-grid,
    &__rights-grid {
      grid-template-columns: 1fr;
    }

    &__hero-frame img {
      height: 220px;
    }

    &__hero-copy h1 {
      font-size: clamp(2.3rem, 13vw, 3.2rem);
    }

    &__rights header {
      align-items: flex-start;
      flex-direction: column;
    }

    &__compliance-grid {
      grid-template-columns: 1fr;
    }

    &__cta {
      text-align: left;

      div {
        justify-content: flex-start;
      }
    }
  }
}
</style>
