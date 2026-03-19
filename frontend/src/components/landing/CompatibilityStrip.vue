<script setup lang="ts">
const tools = [
  { name: 'ChatGPT', logo: '/brands/openai.svg', alt: 'ChatGPT logo', featured: true },
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
      <li v-for="tool in tools" :key="tool.name" class="compat-strip__item" :class="{ 'compat-strip__item--featured': tool.featured }">
        <img
          class="compat-strip__logo"
          :class="{ 'compat-strip__logo--featured': tool.featured }"
          :src="tool.logo"
          :alt="tool.alt"
          :width="tool.featured ? 22 : 18"
          :height="tool.featured ? 22 : 18"
          loading="lazy"
        />
        <span>{{ tool.name }}</span>
        <span v-if="tool.featured" class="compat-strip__badge">Primary</span>
      </li>
    </ul>
    <p class="compat-strip__desc">Use the same sanitisation flow across AI chat, email, and document workflows.</p>
  </section>
</template>

<style scoped lang="scss">
.compat-strip {
  border-radius: 18px;
  background:
    radial-gradient(130% 120% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 66%), transparent 56%),
    color-mix(in srgb, var(--surface-0), white 12%);
  box-shadow: var(--shadow-sm);
  padding: 1.02rem 1.1rem;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 0.72rem 1.08rem;

  &__label {
    margin: 0;
    color: var(--text-3);
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
  }

  &__list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.46rem;
  }

  &__item {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 44%);
    border-radius: 999px;
    background: var(--surface-0);
    color: var(--text-2);
    padding: 0.34rem 0.62rem;
    font-size: 0.8rem;
    font-weight: 600;
    transition: border-color 180ms ease, transform 180ms ease;

    &:hover {
      transform: translateY(-1px);
      border-color: color-mix(in srgb, var(--border-strong), transparent 12%);
      box-shadow: var(--shadow-xs);
    }
  }

  &__item--featured {
    border-color: color-mix(in srgb, var(--accent-2), transparent 30%);
    background: color-mix(in srgb, var(--accent-soft), white 38%);
    color: var(--text-1);
    box-shadow:
      0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 76%),
      var(--shadow-xs);
  }

  &__logo {
    width: 18px;
    height: 18px;
    display: block;
    flex-shrink: 0;
  }

  &__logo--featured {
    width: 22px;
    height: 22px;
  }

  &__badge {
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 52%);
    background: color-mix(in srgb, var(--surface-0), white 8%);
    color: color-mix(in srgb, var(--accent-1), black 8%);
    padding: 0.12rem 0.36rem;
    font-size: 0.66rem;
    line-height: 1;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  &__desc {
    grid-column: 1 / -1;
    margin: 0;
    color: var(--text-3);
    font-size: 0.84rem;
    line-height: 1.5;
  }
}

@media (max-width: 900px) {
  .compat-strip {
    grid-template-columns: 1fr;
    gap: 0.56rem;
  }
}
</style>
