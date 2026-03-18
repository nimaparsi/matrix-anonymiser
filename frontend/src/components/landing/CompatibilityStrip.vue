<script setup lang="ts">
const tools = [
  { name: 'ChatGPT', logo: '/brands/openai.svg', alt: 'ChatGPT logo' },
  { name: 'Claude', logo: '/brands/claude.svg', alt: 'Claude logo' },
  { name: 'Gemini', logo: '/brands/gemini.svg', alt: 'Gemini logo' },
  { name: 'Email', logo: '/brands/gmail.svg', alt: 'Gmail logo' },
  { name: 'Docs', logo: '/brands/googledocs.svg', alt: 'Google Docs logo' },
]
</script>

<template>
  <section class="compat-strip" aria-label="Compatibility">
    <p class="compat-strip__label">Compatible with</p>
    <ul class="compat-strip__list">
      <li v-for="tool in tools" :key="tool.name" class="compat-strip__item">
        <img class="compat-strip__logo" :src="tool.logo" :alt="tool.alt" width="18" height="18" loading="lazy" />
        <span>{{ tool.name }}</span>
      </li>
    </ul>
    <p class="compat-strip__desc">
      Works across AI chat, email, and document workflows with the same sanitisation flow.
    </p>
  </section>
</template>

<style scoped lang="scss">
.compat-strip {
  border: 1px solid color-mix(in srgb, var(--border-1), transparent 16%);
  border-radius: 20px;
  background:
    radial-gradient(100% 130% at 100% 0%, color-mix(in srgb, var(--accent-2), transparent 90%), transparent 45%),
    color-mix(in srgb, var(--surface-glass), transparent 6%);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(14px);
  padding: 0.92rem 1.02rem;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 0.72rem 1rem;

  &__label {
    margin: 0;
    color: var(--text-2);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    white-space: nowrap;
  }

  &__list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.1rem;
  }

  &__item {
    display: inline-flex;
    align-items: center;
    gap: 0.46rem;
    color: var(--text-3);
    font-size: 0.8rem;
    font-weight: 700;
    transition: transform 170ms ease, color 180ms ease;

    &:hover {
      transform: translateY(-1px);
      color: var(--text-1);
    }
  }

  &__logo {
    width: 18px;
    height: 18px;
    display: block;
    flex-shrink: 0;
  }

  &__desc {
    grid-column: 1 / -1;
    margin: 0.08rem 0 0;
    color: var(--text-3);
    font-size: 0.8rem;
    line-height: 1.45;
  }
}

@media (max-width: 900px) {
  .compat-strip {
    grid-template-columns: 1fr;
    gap: 0.58rem;
  }
}
</style>
