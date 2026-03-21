<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="landing-footer" aria-label="Site footer">
    <div class="landing-footer__inner">
      <p>Built by Nima Parsi</p>
      <a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">Open source on GitHub</a>
      <RouterLink to="/privacy">Privacy policy</RouterLink>
      <p>No data stored</p>
      <p>Sensitive data is anonymised before any AI processing.</p>
      <p>Powered by the Matrix Privacy Engine</p>
    </div>
  </footer>
</template>

<style scoped lang="scss">
.landing-footer {
  margin-top: 2.2rem;
  padding-top: 1.2rem;
  border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);

  &__inner {
    display: grid;
    gap: 0.34rem;
    color: var(--text-3);
    font-size: 0.9rem;
    line-height: 1.52;

    p {
      margin: 0;
    }

    a {
      width: fit-content;
      color: var(--text-2);
      text-decoration: none;
      border-bottom: 1px solid color-mix(in srgb, var(--text-2), transparent 60%);
      transition: color 180ms ease, border-color 180ms ease;
    }

    a:hover,
    a:focus-visible {
      color: var(--accent-2);
      border-color: color-mix(in srgb, var(--accent-2), transparent 44%);
    }
  }
}
</style>
