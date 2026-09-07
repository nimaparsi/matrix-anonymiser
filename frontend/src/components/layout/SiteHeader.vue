<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { PhList, PhX } from '@phosphor-icons/vue'

const route = useRoute()
const mobileNavOpen = ref(false)

watch(
  () => route.fullPath,
  () => {
    mobileNavOpen.value = false
  },
)
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

      <button
        class="site-header__menu-btn btn btn--ghost btn--icon"
        type="button"
        :aria-expanded="mobileNavOpen"
        aria-controls="site-nav"
        aria-label="Toggle navigation"
        @click="mobileNavOpen = !mobileNavOpen"
      >
        <PhX v-if="mobileNavOpen" :size="18" weight="bold" aria-hidden="true" />
        <PhList v-else :size="18" weight="bold" aria-hidden="true" />
      </button>

      <nav id="site-nav" class="site-header__nav" :class="{ 'site-header__nav--open': mobileNavOpen }" aria-label="Primary navigation">
        <RouterLink class="site-header__link" to="/tool">Tool</RouterLink>
        <RouterLink class="site-header__link" to="/security">Security</RouterLink>
        <RouterLink class="site-header__link" to="/integrations">Integrations</RouterLink>
        <RouterLink class="site-header__link" to="/privacy">Privacy</RouterLink>
        <RouterLink class="site-header__link" to="/contact">Contact</RouterLink>
      </nav>

      <div class="site-header__actions">
        <RouterLink class="btn btn--primary site-header__cta" to="/tool">
          <span>Open tool</span>
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
  background: color-mix(in srgb, var(--surface-0), white 12%);
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 42%);
  backdrop-filter: saturate(150%) blur(18px);
  -webkit-backdrop-filter: saturate(150%) blur(18px);

  &__inner {
    width: min(1180px, calc(100% - 1.4rem));
    margin: 0 auto;
    min-height: var(--header-h);
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 0.85rem;
  }

  &__brand {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.8rem;
    min-width: 0;

    img {
      width: 42px;
      height: 42px;
      object-fit: contain;
      display: block;
    }

    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(1.35rem, 2vw, 1.78rem);
      letter-spacing: -0.04em;
      color: var(--text-1);
      font-weight: 800;
      line-height: 1;
    }
  }

  &__logo-tile {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(180deg, color-mix(in srgb, var(--surface-1), white 22%), color-mix(in srgb, var(--surface-2), white 10%));
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
  }

  &__menu-btn {
    display: none;
  }

  &__nav {
    display: flex;
    justify-self: center;
    justify-content: center;
    gap: 0.25rem;
  }

  &__link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.84rem;
    font-weight: 650;
    padding: 0.55rem 0.68rem;
    border-radius: 999px;
    transition: color 180ms ease, background 180ms ease;

    &:hover,
    &.router-link-active,
    &.router-link-exact-active,
    &:focus-visible {
      color: var(--accent-1);
      background: color-mix(in srgb, var(--accent-soft), transparent 22%);
    }
  }

  &__actions {
    display: inline-flex;
    align-items: center;
  }

  &__cta {
    min-height: 42px;
    padding-inline: 1rem;
    border-radius: 10px;

    :deep(span) {
      font-size: 0.8rem;
      letter-spacing: -0.01em;
    }
  }
}

@media (max-width: 820px) {
  .site-header {
    &__inner {
      width: min(1180px, calc(100% - 1rem));
      grid-template-columns: auto auto auto;
      gap: 0.65rem;
      padding-block: 0.55rem;
    }

    &__brand {
      gap: 0.62rem;

      strong {
        font-size: clamp(1.18rem, 5vw, 1.44rem);
      }
    }

    &__logo-tile,
    &__brand img {
      width: 38px;
      height: 38px;
      border-radius: 10px;
    }

    &__menu-btn {
      display: inline-flex;
      justify-self: end;
    }

    &__actions {
      justify-self: end;
    }

    &__cta {
      min-height: 38px;
      padding-inline: 0.82rem;

      :deep(span) {
        font-size: 0.76rem;
      }
    }

    &__nav {
      display: none;
      position: absolute;
      top: calc(100% + 0.4rem);
      left: 0.75rem;
      right: 0.75rem;
      flex-direction: column;
      justify-self: stretch;
      gap: 0.2rem;
      padding: 0.5rem;
      border-radius: 16px;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 22%);
      background: color-mix(in srgb, var(--surface-0), white 10%);
      box-shadow: var(--shadow-md);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
    }

    &__nav--open {
      display: flex;
    }

    &__link {
      padding: 0.72rem 0.82rem;
      border-radius: 12px;
      font-size: 0.9rem;
    }
  }
}

@media (max-width: 520px) {
  .site-header {
    &__inner {
      grid-template-columns: auto 1fr auto;
    }

    &__actions {
      display: none;
    }
  }
}
</style>
