<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <div class="site-footer__brand">
        <strong>SanitiseAI</strong>
        <p>Privacy-first text sanitisation for prompts, notes, documents, and operational workflows.</p>
      </div>

      <nav class="site-footer__links" aria-label="Footer links">
        <RouterLink to="/terms">Terms</RouterLink>
        <RouterLink to="/security">Security</RouterLink>
        <RouterLink to="/privacy">Privacy policy</RouterLink>
        <RouterLink to="/contact">Contact</RouterLink>
      </nav>
    </div>
  </footer>
</template>

<style scoped lang="scss">
.site-footer {
  margin-top: 4rem;
  padding: 2.4rem 0 1.8rem;
  border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 42%);
  background: linear-gradient(180deg, color-mix(in srgb, var(--surface-1), white 8%), color-mix(in srgb, var(--surface-0), white 8%));

  &__inner {
    width: min(1200px, calc(100% - 2.4rem));
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.9rem;
  }

  &__brand {
    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: 1.06rem;
      letter-spacing: -0.03em;
      color: var(--text-1);
      font-weight: 780;
    }

    p {
      margin: 0.35rem 0 0;
      max-width: 44ch;
      font-size: 0.82rem;
      color: var(--text-2);
      line-height: 1.6;
      letter-spacing: -0.01em;
      font-weight: 600;
    }
  }

  &__links {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;

    a {
      text-decoration: none;
      color: var(--text-2);
      font-size: 0.78rem;
      font-weight: 650;
      letter-spacing: -0.01em;
      transition: color 180ms ease, opacity 180ms ease;
      opacity: 0.9;

      &:hover,
      &:focus-visible {
        color: var(--accent-1);
        opacity: 1;
      }
    }
  }
}

@media (max-width: 980px) {
  .site-footer {
    margin-top: 2.6rem;

    &__inner {
      width: min(1200px, calc(100% - 1rem));
    }

    &__inner {
      flex-direction: column;
      gap: 0.9rem;
    }
  }
}
</style>
