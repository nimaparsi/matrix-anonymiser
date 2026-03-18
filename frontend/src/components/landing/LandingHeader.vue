<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { PhMoonStars, PhSparkle, PhSun } from '@phosphor-icons/vue'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Use cases', href: '#use-cases' },
  { label: 'Privacy', href: '#privacy' },
]

const QUICK_START_TEXT = 'John Smith from Acme emailed john@acme.com'
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

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme(prefersDark ? 'dark' : 'light', false)
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
        <button class="btn btn--secondary btn--icon landing-header__theme" type="button" :aria-label="`Toggle theme: ${themeLabel}`" @click="toggleTheme">
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
  z-index: 42;
  backdrop-filter: blur(20px) saturate(130%);
  background: color-mix(in srgb, var(--surface-glass), transparent 8%);
  border-bottom: 1px solid var(--border-1);

  &__inner {
    width: min(1160px, calc(100% - 2.4rem));
    margin: 0 auto;
    min-height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.9rem;
  }

  &__brand {
    display: inline-flex;
    align-items: center;
    gap: 0.62rem;
    text-decoration: none;
  }

  &__logo {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    overflow: hidden;
    background: color-mix(in srgb, var(--surface-0), transparent 0%);
    box-shadow:
      0 14px 30px color-mix(in srgb, var(--accent-3), transparent 72%),
      0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 74%);

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
  }

  &__brand-text {
    color: var(--text-1);
    font-family: Sora, Inter, sans-serif;
    font-size: 1.04rem;
    font-weight: 700;
    letter-spacing: -0.012em;
  }

  &__nav {
    display: flex;
    align-items: center;
    gap: 0.22rem;
    padding: 0.24rem;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 20%);
    background: color-mix(in srgb, var(--surface-glass), transparent 6%);
    box-shadow: var(--shadow-xs);
  }

  &__actions {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }

  &__nav-link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.88rem;
    font-weight: 700;
    padding: 0.4rem 0.74rem;
    border-radius: 999px;
    transition:
      color 180ms ease,
      background 180ms ease,
      transform 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--surface-2), var(--accent-2) 9%);
      transform: translateY(-1px);
    }
  }

  &__cta {
    min-height: 40px;
    padding-inline: 0.96rem;
    border-radius: 13px;
  }

  &__theme {
    color: var(--text-1);
  }
}

@media (max-width: 900px) {
  .landing-header {
    &__inner {
      width: min(1160px, calc(100% - 1.4rem));
      min-height: 66px;
    }

    &__brand {
      gap: 0.5rem;
    }

    &__logo {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      box-shadow:
        0 10px 20px color-mix(in srgb, var(--accent-3), transparent 76%),
        0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 74%);
    }

    &__brand-text {
      font-size: 1rem;
    }

    &__nav {
      display: none;
    }

    &__actions {
      gap: 0.4rem;
    }

    &__theme {
      width: 36px;
      height: 36px;
    }

    &__cta {
      border-radius: 12px;
      padding-inline: 0.84rem;
      font-size: 0.86rem;
    }
  }
}

</style>
