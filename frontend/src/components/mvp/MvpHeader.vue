<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { PhArrowRight } from '@phosphor-icons/vue'

const route = useRoute()

const isHome = computed(() => route.name === 'home')
</script>

<template>
  <header class="mvp-header">
    <div class="mvp-header__inner">
      <RouterLink to="/" class="mvp-header__brand" aria-label="SanitiseAI home">
        <strong>SanitiseAI</strong>
      </RouterLink>

      <nav class="mvp-header__nav" aria-label="Primary navigation">
        <RouterLink class="mvp-header__link" to="/tool">Tool</RouterLink>
        <RouterLink class="mvp-header__link" to="/#how-it-works">How it works</RouterLink>
        <a class="mvp-header__link" href="/privacy.html">Privacy</a>
        <RouterLink class="mvp-header__link" to="/integrations">About</RouterLink>
      </nav>

      <RouterLink
        class="btn btn--primary mvp-header__cta"
        :to="{ path: '/tool', query: { demo: '1' } }"
      >
        <span>{{ isHome ? 'Try Sanitiser' : 'Try it free' }}</span>
        <PhArrowRight :size="13" weight="bold" aria-hidden="true" />
      </RouterLink>
    </div>
  </header>
</template>

<style scoped lang="scss">
.mvp-header {
  position: sticky;
  top: 0;
  z-index: 80;
  background: color-mix(in srgb, var(--surface-0), transparent 3%);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);

  &__inner {
    width: min(1200px, calc(100% - 2.4rem));
    margin: 0 auto;
    height: 72px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 1.2rem;
  }

  &__brand {
    text-decoration: none;
    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: 1.86rem;
      letter-spacing: -0.038em;
      color: var(--text-1);
      font-weight: 800;
      line-height: 1;
    }
  }

  &__nav {
    display: inline-flex;
    justify-content: center;
    gap: 0.2rem;
  }

  &__link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.84rem;
    font-weight: 600;
    padding: 0.42rem 0.72rem;
    border-radius: 999px;
    border: 1px solid transparent;
    transition: color 180ms ease, background 180ms ease, border-color 180ms ease;

    &:hover,
    &.router-link-active,
    &.router-link-exact-active,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--surface-1), white 10%);
      border-color: color-mix(in srgb, var(--border-1), transparent 45%);
    }
  }

  &__cta {
    min-height: 42px;
    padding-inline: 0.95rem;
    border-radius: 10px;
  }
}

@media (max-width: 980px) {
  .mvp-header {
    &__inner {
      width: min(1200px, calc(100% - 1rem));
      grid-template-columns: auto auto;
      justify-content: space-between;
      height: 64px;
      gap: 0.5rem;
    }

    &__nav {
      display: none;
    }

    &__cta {
      min-height: 38px;
      padding-inline: 0.8rem;

      :deep(span) {
        font-size: 0.78rem;
      }
    }
  }
}
</style>
