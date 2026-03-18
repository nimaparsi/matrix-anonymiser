<script setup lang="ts">
import { PhCursorText, PhMagicWand, PhShieldCheck } from '@phosphor-icons/vue'

const steps = [
  {
    title: 'Paste your text',
    body: 'Add sensitive notes, contracts, prompts, or copied snippets.',
    icon: PhCursorText,
  },
  {
    title: 'Detect sensitive data',
    body: 'Names, contact details, keys, and identifiers are picked up immediately.',
    icon: PhShieldCheck,
  },
  {
    title: 'Share safe output',
    body: 'Use anonymised text with placeholders while keeping meaning intact.',
    icon: PhMagicWand,
  },
]
</script>

<template>
  <section class="how" aria-labelledby="how-title">
    <header class="how__header">
      <p class="how__eyebrow">How it works</p>
      <h2 id="how-title">Three steps to safe-to-share text</h2>
    </header>

    <ol class="how__steps">
      <li v-for="(step, index) in steps" :key="step.title" class="how__step">
        <div class="how__step-top">
          <span class="how__index">{{ index + 1 }}</span>
          <component :is="step.icon" class="how__icon" :size="20" weight="duotone" aria-hidden="true" />
        </div>
        <h3>{{ step.title }}</h3>
        <p>{{ step.body }}</p>
      </li>
    </ol>
  </section>
</template>

<style scoped lang="scss">
.how {
  &__header {
    h2 {
      margin: 0.5rem 0 0;
      font-size: clamp(1.75rem, 3.8vw, 2.3rem);
      line-height: 1.1;
      letter-spacing: -0.03em;
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

  &__steps {
    list-style: none;
    margin: 1.2rem 0 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
  }

  &__step {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
    border-radius: 16px;
    background:
      radial-gradient(130% 110% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 74%), transparent 52%),
      var(--surface-0);
    box-shadow: var(--shadow-sm);
    padding: 1rem;
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 200ms ease;

    h3 {
      margin: 0.6rem 0 0;
      font-size: 1.03rem;
      color: var(--text-1);
    }

    p {
      margin: 0.46rem 0 0;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.55;
    }

    &:hover {
      transform: translateY(-4px);
      border-color: color-mix(in srgb, var(--border-strong), transparent 12%);
      box-shadow: var(--shadow-md);
    }
  }

  &__step-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
  }

  &__index {
    width: 28px;
    height: 28px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 700;
    color: white;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    box-shadow: var(--shadow-xs);
  }

  &__icon {
    color: var(--accent-2);
  }
}

@media (max-width: 980px) {
  .how {
    &__steps {
      grid-template-columns: 1fr;
    }
  }
}
</style>
