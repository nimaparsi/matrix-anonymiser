<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhBrowsers, PhCode, PhDeviceMobile, PhRocketLaunch, PhRows } from '@phosphor-icons/vue'

const roadmap = [
  {
    title: 'VS Code',
    detail: 'Secure your codebase in real-time. Prevents hardcoding secrets.',
    tag: 'Q3 2024',
  },
  {
    title: 'Google Workspace',
    detail: 'Native DLP for Docs and Sheets. Control data flow easily.',
    tag: 'Q4 2024',
  },
  {
    title: 'Slack',
    detail: 'Integrated message sanitisation for teams.',
    tag: 'Researching',
  },
  {
    title: 'Suggest one',
    detail: 'We build based on user demand.',
    tag: 'Roadmap',
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
        maintain compliance across your primary platforms.
      </p>

      <div class="integrations-page__hero-actions">
        <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
          <PhRocketLaunch :size="16" weight="fill" aria-hidden="true" />
          <span>Launch Web App</span>
        </RouterLink>
        <RouterLink class="btn btn--secondary" to="/tool">View Docs</RouterLink>
      </div>
    </section>

    <section class="integrations-page__grid">
      <article class="integrations-page__card integrations-page__card--wide">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhBrowsers :size="19" weight="duotone" /></span>
          <h2>Chrome &amp; Edge Extension</h2>
        </div>
        <p>
          The universal shield. Automatically detects sensitive data patterns across any web application, from internal
          CRMs to AI portals.
        </p>
        <div class="integrations-page__chips">
          <span>Real-time masking</span>
          <span>Browser native</span>
        </div>
        <RouterLink class="btn btn--primary integrations-page__card-action" to="/tool">
          Install extension
          <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
        </RouterLink>

        <aside class="integrations-page__placeholder" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </aside>
      </article>

      <article class="integrations-page__card">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhDeviceMobile :size="18" weight="duotone" /></span>
          <h2>iOS Mobile App</h2>
        </div>
        <p>Sanitise data on the go. Securely copy-paste text and scrub images before sharing via mobile apps.</p>
        <button class="btn btn--secondary" type="button" disabled>Download for iOS</button>
      </article>

      <article class="integrations-page__card">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhRows :size="18" weight="duotone" /></span>
          <h2>Full Web Dashboard</h2>
        </div>
        <p>Our central hub for scrubbing large documents, managing your custom rulesets, and reviewing history.</p>
        <RouterLink class="btn btn--secondary" to="/tool">Go to App</RouterLink>
      </article>

      <article class="integrations-page__card">
        <div class="integrations-page__card-head">
          <span class="integrations-page__icon"><PhCode :size="18" weight="duotone" /></span>
          <h2>API Integration</h2>
        </div>
        <p>Programmatically scrub data in your own applications. High-performance REST API with zero-log policy.</p>
        <button class="btn btn--secondary" type="button" disabled>Read API Docs</button>
      </article>
    </section>

    <section class="integrations-page__roadmap">
      <header>
        <h3>Upcoming Platforms</h3>
        <p>We're expanding to the tools you use every day.</p>
      </header>
      <ul>
        <li v-for="item in roadmap" :key="item.title">
          <h4>{{ item.title }}</h4>
          <p>{{ item.detail }}</p>
          <small>{{ item.tag }}</small>
        </li>
      </ul>
    </section>

    <section class="integrations-page__final-cta">
      <h2>Ready to secure your workflow?</h2>
      <p>Start sanitising your sensitive data in seconds. No complex setup required for individual use.</p>
      <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">Get Started for Free</RouterLink>
    </section>
  </main>
</template>

<style scoped lang="scss">
.integrations-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.1rem;

  &__eyebrow {
    margin: 0;
    color: var(--accent-1);
    font-size: 0.66rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 760;
  }

  &__hero {
    max-width: 74ch;

    h1 {
      margin-top: 0.8rem;
      font-size: clamp(2.8rem, 7vw, 5.4rem);
      line-height: 0.92;
      letter-spacing: -0.05em;
      font-family: Manrope, Inter, sans-serif;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 1.1rem 0 0;
      max-width: 46ch;
      color: var(--text-2);
      font-size: 1.04rem;
      line-height: 1.64;
    }
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

  &__grid {
    margin-top: 2rem;
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    gap: 0.84rem;
  }

  &__card {
    grid-column: span 6;
    border-radius: 14px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    box-shadow: var(--shadow-xs);
    padding: 1.3rem;
    min-height: 250px;
    display: flex;
    flex-direction: column;

    p {
      margin: 0.84rem 0 0;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.58;
      max-width: 48ch;
    }

    .btn {
      margin-top: auto;
    }
  }

  &__card--wide {
    grid-column: span 8;
    position: relative;
    padding-right: 42%;
  }

  &__card-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;

    h2 {
      margin: 0;
      font-size: 1.95rem;
      font-family: Manrope, Inter, sans-serif;
      line-height: 1.08;
      letter-spacing: -0.03em;
    }
  }

  &__icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    background: color-mix(in srgb, var(--accent-soft), white 40%);
    color: var(--accent-1);
    flex-shrink: 0;
  }

  &__chips {
    margin-top: 0.8rem;
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
    margin-top: 1rem;
    width: fit-content;
  }

  &__placeholder {
    position: absolute;
    right: 1.3rem;
    top: 1.3rem;
    width: min(38%, 232px);
    height: calc(100% - 2.6rem);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-1), white 18%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 42%);
    display: grid;
    align-content: start;
    gap: 0.46rem;
    padding: 0.66rem;

    span {
      height: 8px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent-soft), var(--surface-2) 70%);

      &:nth-child(3) {
        width: 72%;
      }

      &:nth-child(4) {
        width: 52%;
      }
    }
  }

  &__roadmap {
    margin-top: 2rem;

    h3 {
      margin: 0;
      font-size: clamp(1.9rem, 4vw, 2.8rem);
      letter-spacing: -0.03em;
      line-height: 1.05;
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

      li {
        border-radius: 12px;
        padding: 1rem;
        background: color-mix(in srgb, var(--surface-0), var(--surface-1) 42%);
        box-shadow: var(--shadow-xs);

        h4 {
          margin: 0;
          font-size: 1rem;
          line-height: 1.2;
        }

        p {
          margin: 0.66rem 0 0;
          font-size: 0.8rem;
          color: var(--text-3);
          line-height: 1.5;
          min-height: 2.2rem;
        }

        small {
          margin-top: 0.64rem;
          display: inline-flex;
          border-radius: 999px;
          padding: 0.22rem 0.5rem;
          font-size: 0.62rem;
          font-weight: 740;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          color: var(--text-3);
          background: color-mix(in srgb, var(--surface-2), white 8%);
        }
      }
    }
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

    .btn {
      margin-top: 1rem;
      min-width: 180px;
      border-color: color-mix(in srgb, white, transparent 56%);
      background: white;
      color: var(--accent-3);
      box-shadow: none;
    }
  }
}

@media (max-width: 1080px) {
  .integrations-page {
    width: min(1200px, calc(100% - 1rem));

    &__card,
    &__card--wide {
      grid-column: span 12;
      padding-right: 1.3rem;
    }

    &__placeholder {
      display: none;
    }

    &__roadmap ul {
      grid-template-columns: 1fr 1fr;
    }
  }
}

@media (max-width: 680px) {
  .integrations-page {
    &__roadmap ul {
      grid-template-columns: 1fr;
    }
  }
}
</style>
