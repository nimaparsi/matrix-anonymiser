<script setup lang="ts">
import { PhAddressBook, PhEnvelopeSimple, PhGearSix, PhMapPinLine, PhPhone, PhUserList } from '@phosphor-icons/vue'

const featureCards = [
  { title: 'Detect names', body: 'Find and replace personal names with consistent placeholders.', icon: PhUserList },
  { title: 'Mask emails', body: 'Redact email addresses while preserving sentence structure.', icon: PhEnvelopeSimple },
  { title: 'Phone numbers', body: 'Catch common phone formats in support notes and drafts.', icon: PhPhone },
  { title: 'Addresses', body: 'Remove location details before sharing contracts or summaries.', icon: PhMapPinLine },
  { title: 'Documents', body: 'Paste or upload text from notes, reports, and legal docs.', icon: PhAddressBook },
  { title: 'Custom rules', body: 'Switch to custom mode to choose exactly which entities to detect.', icon: PhGearSix },
]
</script>

<template>
  <section class="features" aria-labelledby="features-title">
    <header class="features__header">
      <p class="features__eyebrow">Features</p>
      <h2 id="features-title">Built for practical anonymisation workflows</h2>
    </header>

    <div class="features__grid">
      <article v-for="feature in featureCards" :key="feature.title" class="features__card">
        <div class="features__title-row">
          <component :is="feature.icon" class="features__icon" :size="20" weight="duotone" aria-hidden="true" />
          <h3>{{ feature.title }}</h3>
        </div>
        <p>{{ feature.body }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.features {
  &__header {
    max-width: 720px;

    h2 {
      margin: 0.52rem 0 0;
      font-size: clamp(1.9rem, 4vw, 2.5rem);
      line-height: 1.08;
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

  &__grid {
    margin-top: 1.2rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
  }

  &__card {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: 16px;
    background: var(--surface-0);
    box-shadow: var(--shadow-sm);
    padding: 1rem;
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 200ms ease;

    h3 {
      margin: 0;
      font-size: 1rem;
      color: var(--text-1);
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.54rem 0 0;
      color: var(--text-2);
      line-height: 1.55;
      font-size: 0.92rem;
    }

    &:hover {
      transform: translateY(-4px);
      border-color: color-mix(in srgb, var(--border-strong), transparent 12%);
      box-shadow: var(--shadow-md);
    }
  }

  &__title-row {
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;
  }

  &__icon {
    color: var(--accent-2);
    flex-shrink: 0;
  }
}

@media (max-width: 980px) {
  .features {
    &__grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
}

@media (max-width: 640px) {
  .features {
    &__grid {
      grid-template-columns: 1fr;
    }

    &__card {
      padding: 0.9rem;
    }
  }
}
</style>
