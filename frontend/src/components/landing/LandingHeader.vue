<script setup lang="ts">
const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Use cases', href: '#use-cases' },
  { label: 'Privacy', href: '#privacy' },
]

const QUICK_START_TEXT = 'John Smith from Acme emailed john@acme.com'

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
        <span class="landing-header__logo" aria-hidden="true">S</span>
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

      <button class="landing-header__cta" type="button" @click="runTryItFree">Try it free</button>
    </div>
  </header>
</template>

<style scoped lang="scss">
.landing-header {
  position: sticky;
  top: 0;
  z-index: 30;
  backdrop-filter: blur(12px);
  background: rgba(246, 248, 253, 0.86);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);

  &__inner {
    width: min(1160px, calc(100% - 2.4rem));
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
    gap: 0.58rem;
    text-decoration: none;
  }

  &__logo {
    width: 36px;
    height: 36px;
    border-radius: 11px;
    display: grid;
    place-items: center;
    background: linear-gradient(145deg, #2563eb, #4f46e5);
    color: #fff;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28);
  }

  &__brand-text {
    color: #0f172a;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: -0.01em;
  }

  &__nav {
    display: flex;
    align-items: center;
    gap: 1.2rem;
  }

  &__nav-link {
    text-decoration: none;
    color: #334155;
    font-size: 0.95rem;
    font-weight: 600;
    transition: color 180ms ease;

    &:hover,
    &:focus-visible {
      color: #1d4ed8;
    }
  }

  &__cta {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: linear-gradient(145deg, #2563eb, #4338ca);
    color: #fff;
    border: 0;
    cursor: pointer;
    font-size: 0.93rem;
    font-weight: 700;
    padding: 0.58rem 0.95rem;
    box-shadow: 0 10px 26px rgba(37, 99, 235, 0.3);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 14px 28px rgba(37, 99, 235, 0.34);
    }
  }
}

@media (max-width: 900px) {
  .landing-header {
    &__inner {
      width: min(1160px, calc(100% - 1.4rem));
      min-height: 66px;
    }

    &__nav {
      display: none;
    }
  }
}

</style>
