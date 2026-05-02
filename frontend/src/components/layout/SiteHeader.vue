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
        <RouterLink class="site-header__link" to="/tool">App</RouterLink>
        <RouterLink class="site-header__link" to="/security">Security</RouterLink>
        <RouterLink class="site-header__link" to="/integrations">Integrations</RouterLink>
        <RouterLink class="site-header__link" to="/privacy">Privacy</RouterLink>
        <RouterLink class="site-header__link" to="/contact">Contact</RouterLink>
      </nav>

      <div class="site-header__actions">
        <RouterLink class="btn btn--primary site-header__cta" :to="{ path: '/tool', query: { demo: '1' } }">
          <span>Get Started</span>
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
  background: color-mix(in srgb, var(--surface-0), transparent 3%);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);

  &__inner {
    width: min(1200px, calc(100% - 1.4rem));
    margin: 0 auto;
    height: 82px;
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
      width: 64px;
      height: 64px;
      object-fit: contain;
      display: block;
      margin-top: 0;
      position: static;
      transform: none;
    }

    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(1.95rem, 2.9vw, 2.7rem);
      letter-spacing: -0.035em;
      color: var(--text-1);
      font-weight: 800;
      line-height: 1;
    }
  }

  &__logo-tile {
    width: 64px;
    height: 64px;
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
    gap: 0.78rem;
  }

  &__link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.4rem 0.2rem;
    border-bottom: 1px solid transparent;
    transition: color 180ms ease, border-color 180ms ease, transform 180ms ease;

    &:hover,
    &.router-link-active,
    &.router-link-exact-active,
    &:focus-visible {
      color: var(--accent-1);
      border-bottom-color: color-mix(in srgb, var(--accent-1), transparent 22%);
      transform: translateY(-1px);
    }
  }

  &__actions {
    display: inline-flex;
    align-items: center;
    gap: 0;
  }

  &__cta {
    min-height: 38px;
    padding-inline: 0.86rem;
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
      width: min(1200px, calc(100% - 0.6rem));
      grid-template-columns: auto auto;
      justify-content: space-between;
      height: 68px;
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

    &__brand {
      gap: 0.58rem;

      img {
        width: 46px;
        height: 46px;
        transform: none;
      }

      strong {
        font-size: clamp(1.35rem, 6.4vw, 1.72rem);
      }
    }

    &__logo-tile {
      width: 46px;
      height: 46px;
      border-radius: 0;
    }
  }
}
</style>
