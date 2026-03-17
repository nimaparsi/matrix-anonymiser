<script setup lang="ts">
const steps = [
  {
    title: 'Paste your text',
    body: 'Add notes, prompts, or copied snippets into the workspace.',
  },
  {
    title: 'We detect sensitive data',
    body: 'Names, contact details, and private identifiers are picked up instantly.',
  },
  {
    title: 'Get anonymised results',
    body: 'Copy clean text with placeholders and safely continue your workflow.',
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
        <span class="how__index">{{ index + 1 }}</span>
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
      color: #0f172a;
      font-size: clamp(1.5rem, 3.6vw, 2rem);
      letter-spacing: -0.02em;
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

  &__steps {
    list-style: none;
    margin: 1rem 0 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
  }

  &__step {
    position: relative;
    background: #ffffff;
    border: 1px solid #dbe4f5;
    border-radius: 18px;
    padding: 1rem;

    h3 {
      margin: 0.55rem 0 0;
      color: #0f172a;
      font-size: 1rem;
    }

    p {
      margin: 0.45rem 0 0;
      color: #475569;
      font-size: 0.9rem;
      line-height: 1.5;
    }
  }

  &__index {
    width: 28px;
    height: 28px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    background: linear-gradient(145deg, #2563eb, #4338ca);
    font-size: 0.82rem;
    font-weight: 700;
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
