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
const theme = ref<ThemeMode>('dark')
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
        <button class="btn btn--ghost btn--icon landing-header__theme" type="button" :aria-label="`Toggle theme: ${themeLabel}`" @click="toggleTheme">
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
  border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--surface-glass), transparent 10%),
      color-mix(in srgb, var(--surface-glass), transparent 24%)
    );
  backdrop-filter: blur(18px) saturate(125%);

  &__inner {
    width: min(1240px, calc(100% - 2.2rem));
    margin: 0 auto;
    min-height: 74px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  &__brand {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    text-decoration: none;
  }

  &__logo {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    overflow: hidden;
    display: grid;
    place-items: center;
    box-shadow:
      0 16px 28px color-mix(in srgb, var(--accent-3), transparent 74%),
      0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 78%);

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
  }

  &__brand-text {
    color: var(--text-1);
    font-family: 'Space Grotesk', Inter, sans-serif;
    font-size: 1.04rem;
    font-weight: 700;
    letter-spacing: -0.014em;
  }

  &__nav {
    display: flex;
    align-items: center;
    gap: 0.24rem;
    padding: 0.24rem;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    background: color-mix(in srgb, var(--surface-glass), transparent 12%);
  }

  &__nav-link {
    text-decoration: none;
    color: var(--text-2);
    font-size: 0.86rem;
    font-weight: 700;
    padding: 0.38rem 0.72rem;
    border-radius: 999px;
    transition: color 180ms ease, background 180ms ease, transform 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--surface-2), var(--accent-2) 12%);
      transform: translateY(-1px);
    }
  }

  &__actions {
    display: inline-flex;
    align-items: center;
    gap: 0.48rem;
  }

  &__theme {
    color: var(--text-1);
  }

  &__cta {
    min-height: 40px;
    border-radius: 13px;
    padding-inline: 0.95rem;
  }
}

@media (max-width: 980px) {
  .landing-header {
    &__inner {
      width: min(1240px, calc(100% - 1.2rem));
      min-height: 68px;
    }

    &__nav {
      display: none;
    }

    &__logo {
      width: 36px;
      height: 36px;
      border-radius: 10px;
    }

    &__brand-text {
      font-size: 1rem;
    }

    &__cta {
      padding-inline: 0.82rem;
      font-size: 0.84rem;
    }
  }
}
</style>
