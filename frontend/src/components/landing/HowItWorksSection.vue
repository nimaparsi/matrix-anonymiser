<script setup lang="ts">
import { PhCursorText, PhMagicWand, PhShieldCheck } from '@phosphor-icons/vue'

const steps = [
  {
    title: 'Paste your text',
    body: 'Add notes, prompts, or copied snippets into the workspace.',
    icon: PhCursorText,
  },
  {
    title: 'We detect sensitive data',
    body: 'Names, contact details, and private identifiers are picked up instantly.',
    icon: PhShieldCheck,
  },
  {
    title: 'Get anonymised results',
    body: 'Copy clean text with placeholders and safely continue your workflow.',
    icon: PhMagicWand,
  },
]
</script>

<template>
  <section class="how" aria-labelledby="how-title">
    <header class="how__header">
      <p class="how__eyebrow">How it works</p>
      <h2 id="how-title">Three steps to safe prompts</h2>
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
      margin: 0.42rem 0 0;
      color: var(--text-1);
      font-size: clamp(1.5rem, 3.6vw, 2rem);
      letter-spacing: -0.02em;
    }
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  &__steps {
    list-style: none;
    margin: 1.05rem 0 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.88rem;
  }

  &__step {
    position: relative;
    background:
      radial-gradient(140% 120% at 100% 0%, color-mix(in srgb, var(--accent-2), transparent 90%), transparent 48%),
      linear-gradient(
        170deg,
        color-mix(in srgb, var(--surface-0), white 4%),
        color-mix(in srgb, var(--surface-1), transparent 2%)
      );
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: 20px;
    padding: 1.02rem;
    box-shadow: var(--shadow-sm);
    transition: transform 180ms ease, box-shadow 200ms ease, border-color 200ms ease;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 14px;
      right: 14px;
      height: 1px;
      background: linear-gradient(
        90deg,
        transparent,
        color-mix(in srgb, var(--accent-2), transparent 58%),
        color-mix(in srgb, var(--accent-3), transparent 58%),
        transparent
      );
    }

    h3 {
      margin: 0.58rem 0 0;
      color: var(--text-1);
      font-size: 1.03rem;
    }

    p {
      margin: 0.45rem 0 0;
      color: var(--text-2);
      font-size: 0.91rem;
      line-height: 1.55;
    }

    &:hover {
      transform: translateY(-4px);
      border-color: var(--border-2);
      box-shadow: var(--shadow-md);
    }
  }

  &__step-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
  }

  &__icon {
    color: color-mix(in srgb, var(--accent-2), var(--accent-1) 48%);
    filter: drop-shadow(0 8px 14px color-mix(in srgb, var(--accent-2), transparent 76%));
  }

  &__index {
    width: 28px;
    height: 28px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-ink);
    background: linear-gradient(145deg, var(--accent-1), var(--accent-2));
    font-size: 0.82rem;
    font-weight: 700;
    box-shadow: var(--shadow-xs);
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
