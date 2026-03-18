<script setup lang="ts">
const featureCards = [
  { title: 'Detect Names', body: 'Find and replace personal names with consistent placeholders.', icon: '👤' },
  { title: 'Mask Emails', body: 'Redact email addresses while keeping sentence flow intact.', icon: '✉️' },
  { title: 'Phone Numbers', body: 'Detect common phone formats and anonymise safely.', icon: '📞' },
  { title: 'Addresses', body: 'Remove location details before sharing text externally.', icon: '📍' },
  { title: 'Documents', body: 'Paste or upload text from notes, drafts, and reports.', icon: '🧾' },
  { title: 'Custom Rules', body: 'Toggle built-in controls to match your privacy needs.', icon: '⚙️' },
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
        <div class="features__icon" aria-hidden="true">{{ feature.icon }}</div>
        <h3>{{ feature.title }}</h3>
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
    margin-top: 1.1rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
  }

  &__card {
    background:
      linear-gradient(165deg, color-mix(in srgb, var(--surface-0), white 6%), var(--surface-1));
    border: 1px solid var(--border-1);
    border-radius: 18px;
    padding: 1rem;
    box-shadow: var(--shadow-sm);
    transition: transform 180ms ease, box-shadow 200ms ease, border-color 200ms ease;

    &:nth-child(3n + 1) {
      box-shadow:
        var(--shadow-sm),
        inset 0 2px 0 color-mix(in srgb, var(--accent-1), transparent 78%);
    }

    &:nth-child(3n + 2) {
      box-shadow:
        var(--shadow-sm),
        inset 0 2px 0 color-mix(in srgb, var(--accent-2), transparent 76%);
    }

    &:nth-child(3n) {
      box-shadow:
        var(--shadow-sm),
        inset 0 2px 0 color-mix(in srgb, var(--accent-3), transparent 76%);
    }

    h3 {
      margin: 0.6rem 0 0;
      color: var(--text-1);
      font-size: 1.02rem;
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.52rem 0 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.5;
    }

    &:hover {
      transform: translateY(-2px);
      border-color: var(--border-2);
      box-shadow: var(--shadow-md);
    }
  }

  &__icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    border: 1px solid var(--border-2);
    background: linear-gradient(
      160deg,
      color-mix(in srgb, var(--surface-2), var(--accent-2) 14%),
      color-mix(in srgb, var(--surface-0), transparent 4%)
    );
    font-size: 1rem;
    box-shadow: var(--shadow-xs);
    user-select: none;
    pointer-events: none;
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
