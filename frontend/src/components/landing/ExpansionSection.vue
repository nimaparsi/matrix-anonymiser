<script setup lang="ts">
import { PhBrowser, PhDeviceMobile, PhGoogleChromeLogo } from '@phosphor-icons/vue'

const integrations = ['ChatGPT', 'Claude', 'Gemini', 'Google Docs', 'Gmail']
</script>

<template>
  <section class="expansion" aria-labelledby="expansion-title">
    <header class="expansion__header">
      <p class="expansion__eyebrow">Product expansion</p>
      <h2 id="expansion-title">Use SanitiseAI everywhere</h2>
      <p>Protect prompts and notes before they reach AI tools across desktop and mobile workflows.</p>
    </header>

    <div class="expansion__cards">
      <article class="expansion__card expansion__card--module" aria-label="Chrome extension">
        <div class="expansion__card-top">
          <div class="expansion__title-row">
            <PhGoogleChromeLogo :size="20" weight="duotone" aria-hidden="true" />
            <h3>Chrome extension</h3>
          </div>
          <span class="expansion__pill">Testing beta</span>
        </div>
        <p>Sanitise sensitive text directly inside web workflows before sharing to AI chat tools.</p>
      </article>

      <article class="expansion__card expansion__card--module" aria-label="iOS app">
        <div class="expansion__card-top">
          <div class="expansion__title-row">
            <PhDeviceMobile :size="20" weight="duotone" aria-hidden="true" />
            <h3>iOS app</h3>
          </div>
          <span class="expansion__pill">Testing beta</span>
        </div>
        <p>Sanitise copied text on mobile before sending into ChatGPT, email drafts, or docs.</p>
      </article>

      <article class="expansion__card expansion__card--preview" aria-label="Integration preview">
        <div class="expansion__title-row">
          <PhBrowser :size="18" weight="duotone" aria-hidden="true" />
          <h3>Works inside</h3>
        </div>
        <ul class="expansion__list">
          <li v-for="item in integrations" :key="item">{{ item }}</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.expansion {
  &__header {
    max-width: 720px;

    h2 {
      margin: 0.5rem 0 0;
      font-size: clamp(1.75rem, 3.8vw, 2.3rem);
      line-height: 1.1;
      letter-spacing: -0.03em;
    }

    p {
      margin: 0.62rem 0 0;
      color: var(--text-2);
      font-size: 1rem;
      line-height: 1.6;
    }
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  &__cards {
    margin-top: 1.12rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
  }

  &__card {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 52%);
    border-radius: 16px;
    background:
      radial-gradient(140% 120% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 74%), transparent 52%),
      var(--surface-0);
    box-shadow: var(--shadow-sm);
    padding: 1.06rem;

    h3 {
      margin: 0;
      font-size: 1.02rem;
      color: var(--text-1);
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.56rem 0 0;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.58;
    }
  }

  &__card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.54rem;
  }

  &__title-row {
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;

    :deep(svg) {
      color: var(--accent-2);
      flex-shrink: 0;
    }
  }

  &__pill {
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--border-2), transparent 38%);
    background: color-mix(in srgb, var(--surface-2), transparent 10%);
    color: var(--text-3);
    font-size: 0.7rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 700;
    padding: 0.2rem 0.46rem;
  }

  &__card--module {
    opacity: 0.92;
  }

  &__card--preview {
    display: grid;
    align-content: start;
  }

  &__list {
    list-style: none;
    margin: 0.64rem 0 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.44rem;

    li {
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
      background: color-mix(in srgb, var(--surface-1), transparent 10%);
      padding: 0.28rem 0.56rem;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-2);
    }
  }
}

@media (max-width: 980px) {
  .expansion {
    &__cards {
      grid-template-columns: 1fr;
    }
  }
}
</style>
