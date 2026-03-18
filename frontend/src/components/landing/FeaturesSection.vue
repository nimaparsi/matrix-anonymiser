<script setup lang="ts">
import { PhAddressBook, PhEnvelopeSimple, PhGearSix, PhMapPinLine, PhPhone, PhUserList } from '@phosphor-icons/vue'

const featureCards = [
  { title: 'Detect Names', body: 'Find and replace personal names with consistent placeholders.', icon: PhUserList },
  { title: 'Mask Emails', body: 'Redact email addresses while keeping sentence flow intact.', icon: PhEnvelopeSimple },
  { title: 'Phone Numbers', body: 'Detect common phone formats and anonymise safely.', icon: PhPhone },
  { title: 'Addresses', body: 'Remove location details before sharing text externally.', icon: PhMapPinLine },
  { title: 'Documents', body: 'Paste or upload text from notes, drafts, and reports.', icon: PhAddressBook },
  { title: 'Custom Rules', body: 'Toggle built-in controls to match your privacy needs.', icon: PhGearSix },
]
</script>

<template>
  <section class="features" aria-labelledby="features-title">
    <header class="features__header">
      <p class="features__eyebrow">Features</p>
      <h2 id="features-title">Built for practical anonymisation workflows</h2>
    </header>

    <div class="features__grid">
      <article
        v-for="(feature, index) in featureCards"
        :key="feature.title"
        class="features__card"
        :class="[`features__card--${(index % 3) + 1}`, `features__card--layout-${index + 1}`]"
      >
        <div class="features__title-row">
          <component :is="feature.icon" class="features__icon" :size="21" weight="duotone" aria-hidden="true" />
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
    max-width: 700px;

    h2 {
      margin: 0.45rem 0 0;
      color: var(--text-1);
      font-size: clamp(1.55rem, 3.8vw, 2.2rem);
      letter-spacing: -0.02em;
      line-height: 1.15;
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

  &__grid {
    margin-top: 1.15rem;
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 0.86rem;
  }

  &__card {
    position: relative;
    overflow: hidden;
    background:
      radial-gradient(120% 120% at 100% 0%, color-mix(in srgb, var(--accent-2), transparent 90%), transparent 50%),
      linear-gradient(160deg, color-mix(in srgb, var(--surface-0), white 4%), var(--surface-1));
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: 24px;
    padding: 1.06rem;
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
        color-mix(in srgb, var(--accent-2), transparent 52%),
        color-mix(in srgb, var(--accent-1), transparent 52%),
        transparent
      );
      pointer-events: none;
    }

    &--1 {
      background:
        radial-gradient(140% 120% at 0% 0%, color-mix(in srgb, var(--accent-1), transparent 88%), transparent 52%),
        linear-gradient(160deg, color-mix(in srgb, var(--surface-0), white 3%), var(--surface-1));
    }

    &--layout-1,
    &--layout-4 {
      grid-column: span 3;
    }

    &--layout-2,
    &--layout-3,
    &--layout-5,
    &--layout-6 {
      grid-column: span 2;
    }

    &--2 {
      background:
        radial-gradient(120% 130% at 100% 0%, color-mix(in srgb, var(--accent-2), transparent 88%), transparent 50%),
        linear-gradient(160deg, color-mix(in srgb, var(--surface-0), white 3%), var(--surface-1));
    }

    &--3 {
      background:
        radial-gradient(130% 130% at 50% 0%, color-mix(in srgb, var(--accent-3), transparent 90%), transparent 50%),
        linear-gradient(160deg, color-mix(in srgb, var(--surface-0), white 3%), var(--surface-1));
    }

    h3 {
      margin: 0;
      color: var(--text-1);
      font-size: 1.05rem;
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.56rem 0 0;
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

  &__title-row {
    display: inline-flex;
    align-items: center;
    gap: 0.46rem;
  }

  &__icon {
    color: color-mix(in srgb, var(--accent-2), var(--accent-1) 42%);
    filter: drop-shadow(0 10px 16px color-mix(in srgb, var(--accent-2), transparent 74%));
    flex-shrink: 0;
  }

  @media (max-width: 680px) {
    &__card {
      padding: 0.9rem;
    }
  }
}

@media (max-width: 980px) {
  .features {
    &__grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    &__card {
      grid-column: span 1 !important;
    }
  }
}

@media (max-width: 680px) {
  .features {
    &__grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
