<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { PhMoonStars, PhSparkle, PhSun } from '@phosphor-icons/vue'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Use cases', href: '#use-cases' },
  { label: 'Privacy', href: '#privacy' },
]

const QUICK_START_TEXT = 'John Smith from Acme emailed john@acme.com\nCall me on 07912345678'
type ThemeMode = 'light' | 'dark'
const theme = ref<ThemeMode>('light')
const themeLabel = computed(() => (theme.value === 'dark' ? 'Dark mode' : 'Light mode'))

function applyTheme(nextTheme: ThemeMode, persist = true) {
  theme.value = nextTheme
  document.documentElement.setAttribute('data-theme', nextTheme)
  if (persist) localStorage.setItem('sanitiseai-theme', nextTheme)
}

function toggleTheme() {
  applyTheme(theme.value === 'dark' ? 'light' : 'dark')
}

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

onMounted(() => {
  const saved = localStorage.getItem('sanitiseai-theme')
  if (saved === 'dark' || saved === 'light') {
    applyTheme(saved, false)
    return
  }
  applyTheme('light', false)
})
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
        <button
          class="btn btn--ghost btn--icon landing-header__theme"
          type="button"
          :aria-label="`Toggle theme: ${themeLabel}`"
          @click="toggleTheme"
        >
          <PhSun v-if="theme === 'dark'" :size="18" weight="bold" aria-hidden="true" />
          <PhMoonStars v-else :size="18" weight="bold" aria-hidden="true" />
        </button>
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
    min-height: 76px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.1rem;
  }

  &__brand {
    display: inline-flex;
    align-items: center;
    gap: 0.54rem;
    text-decoration: none;
  }

  &__logo {
    width: 36px;
    height: 36px;
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

  &__brand-text {
    color: var(--text-1);
    font-family: 'Space Grotesk', Manrope, sans-serif;
    font-size: 1.08rem;
    font-weight: 700;
    letter-spacing: -0.022em;
  }

  &__nav {
    display: inline-flex;
    align-items: center;
    gap: 0.14rem;
  }

  &__nav-link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.87rem;
    font-weight: 600;
    letter-spacing: -0.012em;
    padding: 0.44rem 0.76rem;
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
    gap: 0.5rem;
  }

  &__theme {
    color: var(--text-2);
    border-color: color-mix(in srgb, var(--border-1), transparent 24%);
    background: color-mix(in srgb, var(--surface-0), transparent 14%);
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
      min-height: 70px;
    }

    &__nav {
      display: none;
    }

    &__brand-text {
      font-size: 1rem;
    }

    &__logo {
      width: 34px;
      height: 34px;
      border-radius: 10px;
    }

    &__cta {
      min-height: 44px;
      padding-inline: 0.88rem;
      font-size: 0.84rem;
    }
  }
}
</style>
