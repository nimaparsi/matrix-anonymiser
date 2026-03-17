<script setup lang="ts">
const featureCards = [
  { title: 'Detect Names', body: 'Find and replace personal names with consistent placeholders.' },
  { title: 'Mask Emails', body: 'Redact email addresses while keeping sentence flow intact.' },
  { title: 'Phone Numbers', body: 'Detect common phone formats and anonymise safely.' },
  { title: 'Addresses', body: 'Remove location details before sharing text externally.' },
  { title: 'Documents', body: 'Paste or upload text from notes, drafts, and reports.' },
  { title: 'Custom Rules', body: 'Toggle built-in controls to match your privacy needs.' },
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
      color: #0f172a;
      font-size: clamp(1.55rem, 3.8vw, 2.2rem);
      letter-spacing: -0.02em;
      line-height: 1.15;
    }
  }

  &__eyebrow {
    margin: 0;
    color: #1d4ed8;
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
    background: #ffffff;
    border: 1px solid #dbe4f5;
    border-radius: 18px;
    padding: 0.95rem;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    transition: transform 170ms ease, box-shadow 180ms ease;

    h3 {
      margin: 0;
      color: #0f172a;
      font-size: 1.02rem;
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.52rem 0 0;
      color: #475569;
      font-size: 0.9rem;
      line-height: 1.5;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 16px 34px rgba(15, 23, 42, 0.1);
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
