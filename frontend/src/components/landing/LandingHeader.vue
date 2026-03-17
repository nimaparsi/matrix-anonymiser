<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

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
        <button class="landing-header__theme" type="button" :aria-label="`Toggle theme: ${themeLabel}`" @click="toggleTheme">
          <span aria-hidden="true">{{ theme === 'dark' ? '☀️' : '🌙' }}</span>
        </button>
        <button class="landing-header__cta" type="button" @click="runTryItFree">Try it free</button>
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
    width: 42px;
    height: 42px;
    border-radius: 13px;
    display: grid;
    place-items: center;
    overflow: hidden;
    border: 1px solid var(--border-2);
    background: linear-gradient(145deg, color-mix(in srgb, var(--surface-1), white 32%), var(--surface-2));
    box-shadow:
      inset 0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 76%),
      0 14px 28px color-mix(in srgb, var(--accent-3), transparent 72%);

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
    gap: 0.35rem;
    padding: 0.26rem;
    border-radius: 999px;
    border: 1px solid var(--border-1);
    background: color-mix(in srgb, var(--surface-1), transparent 10%);
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
    font-weight: 600;
    padding: 0.4rem 0.72rem;
    border-radius: 999px;
    transition:
      color 180ms ease,
      background 180ms ease,
      transform 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      background: color-mix(in srgb, var(--surface-2), transparent 2%);
      transform: translateY(-1px);
    }
  }

  &__cta {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 13px;
    background: linear-gradient(145deg, var(--accent-1), var(--accent-2));
    color: var(--accent-ink);
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 44%);
    cursor: pointer;
    font-size: 0.88rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    padding: 0.58rem 0.98rem;
    box-shadow:
      0 10px 24px color-mix(in srgb, var(--accent-2), transparent 66%),
      inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 88%);
    transition:
      transform 170ms ease,
      box-shadow 200ms ease,
      filter 200ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      filter: saturate(110%);
      box-shadow:
        0 16px 32px color-mix(in srgb, var(--accent-2), transparent 58%),
        inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 86%);
    }
  }

  &__theme {
    width: 38px;
    height: 38px;
    border-radius: 11px;
    border: 1px solid var(--border-2);
    background: color-mix(in srgb, var(--surface-1), transparent 8%);
    display: inline-grid;
    place-items: center;
    cursor: pointer;
    box-shadow: var(--shadow-xs);
    color: var(--text-1);
    font-size: 0.95rem;
    transition:
      transform 180ms ease,
      border-color 180ms ease,
      box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      border-color: var(--border-2);
      box-shadow: var(--shadow-sm);
    }
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
      width: 34px;
      height: 34px;
      border-radius: 10px;
      box-shadow:
        inset 0 0 0 1px color-mix(in srgb, var(--accent-2), transparent 75%),
        0 8px 18px color-mix(in srgb, var(--accent-2), transparent 82%);
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
      border-radius: 10px;
      font-size: 0.9rem;
    }

    &__cta {
      border-radius: 12px;
      padding: 0.5rem 0.82rem;
      font-size: 0.86rem;
      box-shadow:
        0 10px 20px color-mix(in srgb, var(--accent-2), transparent 70%),
        inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 88%);
    }
  }
}

</style>
