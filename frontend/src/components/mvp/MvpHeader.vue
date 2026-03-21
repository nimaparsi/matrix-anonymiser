<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { PhGearSix, PhUserCircle } from '@phosphor-icons/vue'
</script>

<template>
  <header class="mvp-header">
    <div class="mvp-header__inner">
      <RouterLink to="/" class="mvp-header__brand" aria-label="SanitiseAI home">
        <img src="/sanitise-ai-face-512.png" alt="" />
        <strong>SanitiseAI</strong>
      </RouterLink>

      <nav class="mvp-header__nav" aria-label="Primary navigation">
        <RouterLink class="mvp-header__link" to="/tool">App</RouterLink>
        <RouterLink class="mvp-header__link" to="/privacy">Security</RouterLink>
        <RouterLink class="mvp-header__link" to="/integrations">Integrations</RouterLink>
        <a class="mvp-header__link" href="mailto:nimaparsi@icloud.com">Company</a>
      </nav>

      <div class="mvp-header__actions">
        <button class="mvp-header__icon-btn" type="button" aria-label="Settings">
          <PhGearSix :size="14" weight="fill" aria-hidden="true" />
        </button>
        <a class="mvp-header__icon-btn" href="mailto:nimaparsi@icloud.com" aria-label="Contact company">
          <PhUserCircle :size="14" weight="fill" aria-hidden="true" />
        </a>

        <RouterLink class="btn btn--primary mvp-header__cta" :to="{ path: '/tool', query: { demo: '1' } }">
          <span>Get Started</span>
        </RouterLink>
      </div>
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
    gap: 1rem;
  }

  &__brand {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.48rem;

    img {
      width: 18px;
      height: 18px;
      object-fit: contain;
      display: block;
    }

    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: 1.98rem;
      letter-spacing: -0.04em;
      color: var(--text-1);
      font-weight: 800;
      line-height: 1;
    }
  }

  &__nav {
    display: inline-flex;
    justify-content: center;
    gap: 0.64rem;
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
    gap: 0.4rem;
  }

  &__icon-btn {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    border: none;
    background: transparent;
    color: var(--text-2);
    display: inline-grid;
    place-items: center;
    padding: 0;
    text-decoration: none;
    cursor: pointer;
    transition: color 180ms ease, transform 180ms ease, background 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--surface-1), white 6%);
      transform: translateY(-1px) scale(1.03);
      outline: none;
    }
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

    &__brand {
      img {
        width: 16px;
        height: 16px;
      }

      strong {
        font-size: 1.7rem;
      }
    }

    &__icon-btn {
      display: none;
    }
  }
}
</style>
