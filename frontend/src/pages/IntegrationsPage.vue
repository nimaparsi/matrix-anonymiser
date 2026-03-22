<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhBrowsers, PhCode, PhDeviceMobile, PhRocketLaunch, PhRows } from '@phosphor-icons/vue'

const ecosystem = [
  {
    title: 'ChatGPT Plugin',
    detail: 'Safely send prompts to OpenAI. We strip proprietary code and PII instantly.',
    badge: 'Active',
    tone: 'active',
    glyph: 'GP',
  },
  {
    title: 'LLM Proxy',
    detail: 'Enterprise-grade proxy for Anthropic and Google models with full audit logs.',
    badge: 'Active',
    tone: 'active',
    glyph: 'LP',
  },
  {
    title: 'Slack Enterprise',
    detail: 'Real-time channel monitoring and sensitive data masking for workspaces.',
    badge: 'Active',
    tone: 'active',
    glyph: 'SE',
  },
  {
    title: 'VS Code',
    detail: 'Secure your codebase in real-time. Prevents hardcoding secrets.',
    badge: 'Q3 2026',
    tone: 'plan',
    glyph: 'VS',
  },
  {
    title: 'Google Workspace',
    detail: 'Native DLP for Docs and Sheets. Control data flow in collaboration.',
    badge: 'Q4 2026',
    tone: 'plan',
    glyph: 'GW',
  },
  {
    title: 'Outlook',
    detail: 'Integrated email sanitisation. Automatically scrub attachments.',
    badge: 'Researching',
    tone: 'research',
    glyph: 'OL',
  },
  {
    title: 'Suggest More',
    detail: 'We build based on user demand.',
    badge: '',
    tone: 'empty',
    glyph: '+',
  },
]
</script>

<template>
  <main class="integrations-page">
    <section class="integrations-page__hero">
      <p class="integrations-page__eyebrow">The ecosystem</p>
      <h1>
        Your privacy,<br />
        <span>everywhere you work.</span>
      </h1>
      <p>
        SanitiseAI embeds directly into your existing workflows. Automatically scrub PII, mask sensitive data, and
        maintain compliance without leaving your favorite tools.
      </p>

      <div class="integrations-page__hero-actions">
        <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
          <PhRocketLaunch :size="16" weight="fill" aria-hidden="true" />
          <span>Launch Web App</span>
        </RouterLink>
        <RouterLink class="btn btn--secondary" to="/tool">View Docs</RouterLink>
      </div>
    </section>

    <section class="integrations-page__platform-grid">
      <article class="integrations-page__card integrations-page__card--wide">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhRows :size="18" weight="duotone" /></span>
          <h2>Web App</h2>
        </div>
        <p>
          The full SanitiseAI experience in your browser. Upload documents, manage team policies, and scrub data through
          our powerful cloud interface.
        </p>
        <div class="integrations-page__chips">
          <span>Dashboard</span>
          <span>Team management</span>
        </div>
        <RouterLink class="btn btn--primary integrations-page__card-action" to="/tool">Try Web App</RouterLink>
      </article>

      <article class="integrations-page__card">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhBrowsers :size="18" weight="duotone" /></span>
          <h2>Chrome &amp; Edge</h2>
        </div>
        <p>The universal shield. Automatically detects sensitive data patterns across any web application you visit.</p>
        <RouterLink class="integrations-page__text-link" to="/tool">
          Add to Browser
          <PhArrowRight :size="12" weight="bold" aria-hidden="true" />
        </RouterLink>
      </article>

      <article class="integrations-page__card integrations-page__card--small">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhDeviceMobile :size="18" weight="duotone" /></span>
          <h2>iOS App</h2>
        </div>
        <p>Secure communication on the go. Native iOS integration for mobile privacy and secure copy-paste workflows.</p>
        <button class="btn btn--secondary integrations-page__ghost-btn" type="button" disabled>
          Download on App Store
        </button>
      </article>

      <article class="integrations-page__card integrations-page__card--small integrations-page__card--wide">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhCode :size="18" weight="duotone" /></span>
          <h2>API Integration</h2>
        </div>
        <p>Programmatically scrub data in your own applications. High-performance REST API with zero-log policy.</p>
        <button class="btn btn--secondary integrations-page__ghost-btn" type="button" disabled>Read API docs</button>
      </article>
    </section>

    <section class="integrations-page__ecosystem">
      <header>
        <h3>The Ecosystem</h3>
        <p>Connect SanitiseAI to every corner of your professional stack.</p>
      </header>

      <ul>
        <li v-for="item in ecosystem" :key="item.title" class="integrations-page__eco-card">
          <span class="integrations-page__eco-glyph" :class="`integrations-page__eco-glyph--${item.tone}`">{{ item.glyph }}</span>
          <h4>{{ item.title }}</h4>
          <p>{{ item.detail }}</p>
          <small v-if="item.badge" :class="`integrations-page__eco-badge integrations-page__eco-badge--${item.tone}`">
            {{ item.badge }}
          </small>
        </li>
      </ul>
    </section>

    <section class="integrations-page__final-cta">
      <h2>Ready to secure your entire workflow?</h2>
      <p>Join privacy-focused teams using SanitiseAI to manage sensitive text automatically.</p>
      <div class="integrations-page__cta-actions">
        <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Get Started for Free</RouterLink>
        <a class="btn btn--ghost" href="mailto:nimaparsi@icloud.com">Contact Enterprise Sales</a>
      </div>
    </section>
  </main>
</template>

<style scoped lang="scss">
.integrations-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.1rem;

  &__hero {
    max-width: 78ch;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-1);
    font-size: 0.66rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 760;
  }

  h1 {
    margin-top: 0.8rem;
    font-size: clamp(2.8rem, 6vw, 4.8rem);
    line-height: 0.95;
    letter-spacing: -0.05em;
    font-family: Manrope, Inter, sans-serif;

    span {
      color: var(--accent-1);
    }
  }

  &__hero p {
    margin: 1.1rem 0 0;
    max-width: 47ch;
    color: var(--text-2);
    font-size: 1rem;
    line-height: 1.62;
  }

  &__hero-actions {
    margin-top: 1.3rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;

    .btn {
      min-height: 50px;
      padding-inline: 1.2rem;
    }
  }

  &__platform-grid {
    margin-top: 2rem;
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    gap: 0.84rem;
  }

  &__card {
    grid-column: span 4;
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 32%);
    box-shadow: var(--shadow-xs);
    padding: 1.2rem;
    min-height: 246px;
    display: flex;
    flex-direction: column;

    h2 {
      margin: 0;
      font-size: 2rem;
      letter-spacing: -0.03em;
      line-height: 1;
      font-family: Manrope, Inter, sans-serif;
    }

    p {
      margin: 0.85rem 0 0;
      color: var(--text-2);
      font-size: 0.91rem;
      line-height: 1.58;
      max-width: 48ch;
    }
  }

  &__card--wide {
    grid-column: span 8;
  }

  &__card--small {
    min-height: 210px;
  }

  &__card-head {
    display: flex;
    align-items: center;
    gap: 0.56rem;
  }

  &__icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    color: var(--accent-1);
    background: color-mix(in srgb, var(--accent-soft), white 38%);
    flex-shrink: 0;
  }

  &__chips {
    margin-top: 0.82rem;
    display: inline-flex;
    gap: 0.4rem;
    flex-wrap: wrap;

    span {
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-2), white 10%);
      color: var(--text-3);
      font-size: 0.62rem;
      letter-spacing: 0.06em;
      font-weight: 740;
      text-transform: uppercase;
      padding: 0.28rem 0.54rem;
    }
  }

  &__card-action {
    margin-top: auto;
    width: fit-content;
  }

  &__text-link {
    margin-top: auto;
    width: fit-content;
    display: inline-flex;
    align-items: center;
    gap: 0.36rem;
    color: var(--accent-1);
    text-decoration: none;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: -0.01em;
  }

  &__ghost-btn {
    margin-top: auto;
    width: 100%;
    justify-content: center;
  }

  &__ecosystem {
    margin-top: 2.2rem;

    h3 {
      margin: 0;
      font-size: clamp(1.9rem, 4vw, 2.8rem);
      letter-spacing: -0.03em;
      line-height: 1.06;
    }

    p {
      margin: 0.55rem 0 0;
      color: var(--text-2);
      font-size: 0.95rem;
    }

    ul {
      margin: 1rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.84rem;
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }

  &__eco-card {
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 32%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 42%);
    box-shadow: var(--shadow-xs);

    h4 {
      margin: 0.54rem 0 0;
      font-size: 0.96rem;
      line-height: 1.2;
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.64rem 0 0;
      font-size: 0.78rem;
      color: var(--text-3);
      line-height: 1.48;
      min-height: 2.36rem;
    }
  }

  &__eco-glyph {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    font-size: 0.6rem;
    font-weight: 760;
    letter-spacing: 0.02em;
    color: var(--text-1);
    background: color-mix(in srgb, var(--surface-2), white 8%);
  }

  &__eco-glyph--active {
    color: #065f46;
    background: #d1fae5;
  }

  &__eco-glyph--plan {
    color: var(--accent-3);
    background: color-mix(in srgb, var(--accent-soft), white 22%);
  }

  &__eco-glyph--research {
    color: #6b7280;
    background: #e5e7eb;
  }

  &__eco-glyph--empty {
    color: var(--accent-1);
    background: color-mix(in srgb, var(--accent-soft), white 36%);
  }

  &__eco-badge {
    margin-top: 0.66rem;
    display: inline-flex;
    border-radius: 999px;
    padding: 0.22rem 0.5rem;
    font-size: 0.6rem;
    font-weight: 740;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  &__eco-badge--active {
    color: #166534;
    background: #dcfce7;
  }

  &__eco-badge--plan {
    color: var(--accent-3);
    background: color-mix(in srgb, var(--accent-soft), white 12%);
  }

  &__eco-badge--research {
    color: #4b5563;
    background: #e5e7eb;
  }

  &__final-cta {
    margin-top: 2.2rem;
    border-radius: 18px;
    background: linear-gradient(180deg, #406ff7, #2f62f5);
    color: white;
    text-align: center;
    padding: clamp(2rem, 5vw, 3.1rem);

    h2 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.02;
      letter-spacing: -0.04em;
      color: inherit;
    }

    p {
      margin: 0.94rem auto 0;
      max-width: 54ch;
      color: color-mix(in srgb, white, transparent 16%);
      font-size: 0.96rem;
      line-height: 1.58;
    }
  }

  &__cta-actions {
    margin-top: 1rem;
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;

    .btn {
      min-width: 190px;
    }

    .btn--secondary {
      border-color: color-mix(in srgb, white, transparent 56%);
      background: white;
      color: var(--accent-3);
      box-shadow: none;
    }

    .btn--ghost {
      color: white;
      border-color: color-mix(in srgb, white, transparent 56%);
      background: transparent;
    }
  }
}

@media (max-width: 1080px) {
  .integrations-page {
    width: min(1200px, calc(100% - 1rem));

    &__card,
    &__card--wide {
      grid-column: span 12;
    }

    &__ecosystem ul {
      grid-template-columns: 1fr 1fr;
    }
  }
}

@media (max-width: 680px) {
  .integrations-page {
    &__ecosystem ul {
      grid-template-columns: 1fr;
    }
  }
}
</style>
