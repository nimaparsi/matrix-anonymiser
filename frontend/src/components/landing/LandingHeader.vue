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
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    overflow: hidden;
    border: 1px solid rgba(59, 130, 246, 0.22);
    background: linear-gradient(145deg, #eef4ff, #dbeafe);
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
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
    border-radius: 14px;
    background: linear-gradient(145deg, #4f46e5, #2563eb);
    color: #fff;
    border: 1px solid rgba(67, 56, 202, 0.35);
    cursor: pointer;
    font-size: 0.92rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    padding: 0.6rem 1.02rem;
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.32);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 18px 32px rgba(37, 99, 235, 0.4);
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
      box-shadow: 0 8px 18px rgba(37, 99, 235, 0.16);
    }

    &__brand-text {
      font-size: 1rem;
    }

    &__nav {
      display: none;
    }

    &__cta {
      border-radius: 12px;
      padding: 0.52rem 0.86rem;
      font-size: 0.86rem;
      box-shadow: 0 10px 20px rgba(37, 99, 235, 0.26);
    }
  }
}

</style>
