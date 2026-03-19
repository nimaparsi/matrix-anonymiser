<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { PhArrowRight, PhShieldCheck } from '@phosphor-icons/vue'

const route = useRoute()

const isHome = computed(() => route.name === 'home')
</script>

<template>
  <header class="mvp-header">
    <div class="mvp-header__inner">
      <RouterLink to="/" class="mvp-header__brand" aria-label="SanitiseAI home">
        <span class="mvp-header__logo" aria-hidden="true">
          <img src="/sanitise-ai-face-512.png" alt="" />
        </span>
        <span class="mvp-header__brand-copy">
          <strong>SanitiseAI</strong>
          <small>MVP</small>
        </span>
      </RouterLink>

      <nav class="mvp-header__nav" aria-label="Primary navigation">
        <RouterLink class="mvp-header__link" to="/">Home</RouterLink>
        <RouterLink class="mvp-header__link" to="/tool">Tool</RouterLink>
        <RouterLink class="mvp-header__link" to="/integrations">Integrations</RouterLink>
        <a class="mvp-header__link" href="/privacy.html">Privacy</a>
      </nav>

      <RouterLink
        class="btn btn--primary mvp-header__cta"
        :to="{ path: '/tool', query: { demo: '1' } }"
      >
        <PhShieldCheck :size="16" weight="fill" aria-hidden="true" />
        <span>{{ isHome ? 'Start sanitising' : 'Try it free' }}</span>
        <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
      </RouterLink>
    </div>
  </header>
</template>

<style scoped lang="scss">
.mvp-header {
  position: sticky;
  top: 0;
  z-index: 60;
  backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--surface-0), transparent 8%);
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 35%);

  &__inner {
    width: min(1200px, calc(100% - 2.8rem));
    margin: 0 auto;
    height: 78px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 1.4rem;
  }

  &__brand {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.68rem;
  }

  &__logo {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-xs);

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
  }

  &__brand-copy {
    display: inline-flex;
    align-items: baseline;
    gap: 0.4rem;

    strong {
      font-family: 'Space Grotesk', Manrope, sans-serif;
      font-size: 1.08rem;
      letter-spacing: -0.022em;
      color: var(--text-1);
      font-weight: 700;
    }

    small {
      border-radius: 999px;
      padding: 0.14rem 0.38rem;
      background: color-mix(in srgb, var(--accent-soft), white 40%);
      color: var(--accent-3);
      font-size: 0.62rem;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
  }

  &__nav {
    display: inline-flex;
    justify-content: center;
    gap: 0.24rem;
  }

  &__link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.9rem;
    font-weight: 650;
    padding: 0.48rem 0.82rem;
    border-radius: 999px;
    transition: color 180ms ease, background 180ms ease;

    &:hover,
    &.router-link-active,
    &.router-link-exact-active,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--accent-soft), var(--surface-0) 42%);
    }
  }

  &__cta {
    min-height: 46px;
    padding-inline: 1rem;
  }
}

@media (max-width: 980px) {
  .mvp-header {
    &__inner {
      width: min(1200px, calc(100% - 1.2rem));
      grid-template-columns: auto auto;
      justify-content: space-between;
      height: 70px;
      gap: 0.8rem;
    }

    &__nav {
      display: none;
    }

    &__cta {
      min-height: 42px;
      padding-inline: 0.8rem;

      :deep(span) {
        font-size: 0.82rem;
      }
    }
  }
}
</style>
