<script setup lang="ts">
import { PhSparkle } from '@phosphor-icons/vue'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Use cases', href: '#use-cases' },
  { label: 'Security', href: '/security' },
  { label: 'Privacy', href: '#privacy' },
]

const QUICK_START_TEXT = 'John Smith from Acme emailed john@acme.com\nCall me on 07912345678'
function runTryItFree() {
  document.getElementById('demo')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })

  window.setTimeout(() => {
    window.dispatchEvent(
      new CustomEvent('sanitiseai:try-example', {
        detail: {
          quickStart: true,
          text: QUICK_START_TEXT,
          instant: true,
          focus: true,
        },
      }),
    )
  }, 120)
}
</script>

<template>
  <header class="landing-header">
    <div class="landing-header__inner">
      <a class="landing-header__brand" href="#demo" aria-label="SanitiseAI home">
        <span class="landing-header__logo" aria-hidden="true">
          <img src="/sanitise-ai-face-512.png" alt="" />
        </span>
        <span class="landing-header__brand-text">SanitiseAI</span>
      </a>

      <nav class="landing-header__nav" aria-label="Primary">
        <a
          v-for="link in navLinks"
          :key="link.href"
          class="landing-header__nav-link"
          :href="link.href"
        >
          {{ link.label }}
        </a>
      </nav>

      <div class="landing-header__actions">
        <button class="btn btn--primary landing-header__cta" type="button" @click="runTryItFree">
          <PhSparkle :size="15" weight="fill" aria-hidden="true" />
          <span>Try it free</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
.landing-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: color-mix(in srgb, var(--surface-0), transparent 14%);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 35%);

  &__inner {
    width: min(1220px, calc(100% - 3.2rem));
    margin: 0 auto;
    min-height: 108px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.1rem;
  }

  &__brand {
    display: inline-flex;
    align-items: center;
    gap: 0.9rem;
    text-decoration: none;
  }

  &__logo {
    width: 82px;
    height: 82px;
    border-radius: 0;
    background: #e9ebef;
    overflow: hidden;
    border-right: 1px solid color-mix(in srgb, var(--border-1), transparent 22%);
    display: inline-flex;
    align-items: center;
    justify-content: center;

    img {
      width: 70px;
      height: 70px;
      object-fit: contain;
      display: block;
    }
  }

  &__brand-text {
    color: var(--text-1);
    font-family: 'Space Grotesk', Manrope, sans-serif;
    font-size: clamp(2rem, 2.8vw, 3.1rem);
    font-weight: 700;
    letter-spacing: -0.038em;
    line-height: 1;
  }

  &__nav {
    display: inline-flex;
    align-items: center;
    gap: 0.14rem;
  }

  &__nav-link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: -0.012em;
    padding: 0.44rem 0.62rem;
    border-radius: 999px;
    transition: background 180ms ease, color 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--accent-soft), var(--surface-0) 50%);
    }
  }

  &__actions {
    display: inline-flex;
    align-items: center;
    gap: 0.62rem;
  }

  &__cta {
    min-height: 48px;
    padding-inline: 1.18rem;
  }
}

@media (max-width: 980px) {
  .landing-header {
    &__inner {
      width: min(1220px, calc(100% - 1.4rem));
      min-height: 86px;
    }

    &__nav {
      display: none;
    }

    &__brand-text {
      font-size: clamp(1.45rem, 7vw, 1.84rem);
    }

    &__logo {
      width: 64px;
      height: 64px;
      border-right: none;

      img {
        width: 52px;
        height: 52px;
      }
    }

    &__cta {
      min-height: 44px;
      padding-inline: 0.88rem;
      font-size: 0.84rem;
    }
  }
}
</style>
