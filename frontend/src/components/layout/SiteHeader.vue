<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="site-header">
    <div class="site-header__inner">
      <RouterLink to="/" class="site-header__brand" aria-label="SanitiseAI home">
        <span class="site-header__logo-tile" aria-hidden="true">
          <img src="/sanitise-ai-face-512.png" alt="" />
        </span>
        <strong>SanitiseAI</strong>
      </RouterLink>

      <nav class="site-header__nav" aria-label="Primary navigation">
        <RouterLink class="site-header__link" to="/tool">Sanitiser</RouterLink>
        <RouterLink class="site-header__link" to="/security">Security</RouterLink>
        <RouterLink class="site-header__link" to="/integrations">Integrations</RouterLink>
        <RouterLink class="site-header__link" to="/privacy">Privacy</RouterLink>
        <RouterLink class="site-header__link" to="/contact">Contact</RouterLink>
      </nav>

      <div class="site-header__actions">
        <RouterLink class="btn btn--primary site-header__cta" :to="{ path: '/tool', query: { demo: '1' } }">
          <span>Try demo</span>
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
.site-header {
  position: sticky;
  top: 0;
  z-index: 80;
  background: var(--surface-0);
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);

  &__inner {
    width: min(1200px, calc(100% - 1.4rem));
    margin: 0 auto;
    height: 74px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 0.6rem;
  }

  &__brand {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    overflow: visible;

    img {
      width: 52px;
      height: 52px;
      object-fit: contain;
      display: block;
      margin-top: 0;
      position: static;
      transform: none;
    }

    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(1.55rem, 2.4vw, 2rem);
      letter-spacing: 0;
      color: var(--text-1);
      font-weight: 800;
      line-height: 1;
    }
  }

  &__logo-tile {
    width: 52px;
    height: 52px;
    border-radius: 0;
    background: transparent;
    border-right: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: visible;
    box-shadow: none;
    flex-shrink: 0;
    margin-left: 0;
  }

  &__nav {
    display: flex;
    justify-self: center;
    align-self: center;
    justify-content: center;
    gap: 0.46rem;
  }

  &__link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.52rem 0.64rem;
    border-radius: var(--radius-sm);
    transition: color 180ms ease, background 180ms ease;

    &:hover,
    &.router-link-active,
    &.router-link-exact-active,
    &:focus-visible {
      color: var(--accent-1);
      background: color-mix(in srgb, var(--accent-soft), transparent 24%);
    }
  }

  &__actions {
    display: inline-flex;
    align-items: center;
    gap: 0;
  }

  &__cta {
    min-height: 40px;
    padding-inline: 0.9rem;
    border-radius: 8px;

    :deep(span) {
      font-size: 0.76rem;
      letter-spacing: -0.01em;
    }
  }
}

@media (max-width: 980px) {
  .site-header {
    &__inner {
      width: min(1200px, calc(100% - 0.75rem));
      grid-template-columns: auto minmax(0, 1fr) auto;
      height: auto;
      min-height: 66px;
      gap: 0.5rem;
    }

    &__nav {
      justify-self: start;
      justify-content: flex-start;
      gap: 0.2rem;
      overflow-x: auto;
      scrollbar-width: none;

      &::-webkit-scrollbar {
        display: none;
      }
    }

    &__link {
      white-space: nowrap;
      font-size: 0.74rem;
      padding: 0.44rem 0.5rem;
    }

    &__cta {
      min-height: 38px;
      padding-inline: 0.8rem;

      :deep(span) {
        font-size: 0.78rem;
      }
    }

    &__brand {
      gap: 0.58rem;

      img {
        width: 46px;
        height: 46px;
        transform: none;
      }

      strong {
        font-size: clamp(1.18rem, 5.2vw, 1.46rem);
      }
    }

    &__logo-tile {
      width: 46px;
      height: 46px;
      border-radius: 0;
    }
  }
}

@media (max-width: 620px) {
  .site-header {
    &__inner {
      grid-template-columns: 1fr auto;
      padding-block: 0.42rem;
    }

    &__nav {
      grid-column: 1 / -1;
      width: 100%;
      order: 3;
      padding-bottom: 0.34rem;
    }

    &__brand img,
    &__logo-tile {
      width: 40px;
      height: 40px;
    }
  }
}
</style>
