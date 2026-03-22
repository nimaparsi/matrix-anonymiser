<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhLock, PhShieldCheck, PhSparkle } from '@phosphor-icons/vue'

let revealObserver: IntersectionObserver | null = null

onMounted(() => {
  const targets = Array.from(document.querySelectorAll<HTMLElement>('[data-reveal]'))
  if (!targets.length) return

  revealObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          revealObserver?.unobserve(entry.target)
        }
      }
    },
    { threshold: 0.2, rootMargin: '0px 0px -6% 0px' },
  )

  targets.forEach((target) => revealObserver?.observe(target))

})

onBeforeUnmount(() => {
  revealObserver?.disconnect()
  revealObserver = null
})
</script>

<template>
  <main class="home-page">
    <section class="home-page__hero">
      <div class="home-page__hero-copy" data-reveal>
        <p class="home-page__hero-tag">Sanitise before you share • Privacy by design</p>
        <h1>
          Protect your <span>data</span><br />
          without compromise.
        </h1>
        <p>
          The world’s most advanced data sanitisation tool. Anonymise sensitive information locally in your browser. No
          accounts, no data logging, no cloud storage.
        </p>

        <div class="home-page__hero-actions">
          <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
            <span>Start sanitising now</span>
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
          <RouterLink class="btn btn--secondary" :to="{ path: '/tool', query: { demo: '1' } }">View Demo</RouterLink>
        </div>

        <div class="home-page__social-proof">
          <div class="home-page__avatars" aria-hidden="true">
            <span>A</span>
            <span>N</span>
            <span>P</span>
          </div>
          <p>Used by 10k+ security-conscious professionals</p>
        </div>
      </div>

      <article class="home-page__hero-visual" aria-label="Sanitisation flow preview" data-reveal>
        <p class="home-page__visual-eyebrow">Local-first execution</p>

        <div class="home-page__visual-block home-page__visual-block--raw">
          <small>Input source</small>
          <code>{ "user": "John Doe", "email": "john.doe@example.com", "ssn": "999-01-2234" }</code>
        </div>

        <div class="home-page__line home-page__line--blue"></div>

        <div class="home-page__visual-shield" aria-live="polite">
          <div class="home-page__shield-pulse" aria-hidden="true">
            <PhShieldCheck :size="18" weight="fill" aria-hidden="true" />
          </div>
          <small>Sanitising layer active</small>
          <strong>Processing stream...</strong>
          <div class="home-page__shield-stream" aria-hidden="true">
            <span style="width: 72%"></span>
          </div>
          <div class="home-page__shield-labels" aria-hidden="true">
            <span>Scanning</span>
            <span>Anonymizing</span>
          </div>
        </div>

        <div class="home-page__line home-page__line--green"></div>

        <div class="home-page__visual-block home-page__visual-block--safe">
          <small>Protected output</small>
          <code>{ "user": "[ANONYMISED]", "email": "j***@********.com", "ssn": "[REDACTED]" }</code>
        </div>
      </article>
    </section>

    <section id="how-it-works" class="home-page__standard" data-reveal>
      <header class="home-page__section-head">
        <p>The sanitise standard</p>
        <h2>Privacy that works for you.</h2>
      </header>

      <div class="home-page__feature-grid">
        <article class="home-page__feature home-page__feature--wide" data-reveal>
          <PhSparkle :size="24" weight="duotone" aria-hidden="true" />
          <h3>100% Client-Side</h3>
          <p>
            Processing happens entirely in your browser memory. We never see your data, and we don't have a database to
            store it even if we wanted to. Pure technical privacy.
          </p>
          <div class="home-page__chips">
            <span>Immediate results</span>
            <span>Zero accounts</span>
          </div>
        </article>

        <article class="home-page__feature home-page__feature--accent" data-reveal>
          <PhLock :size="26" weight="fill" aria-hidden="true" />
          <h3>No Barriers</h3>
          <p>No “Sign up to view results”. No email wall. No credit cards. Just paste, sanitise, and go.</p>
        </article>

        <article class="home-page__feature" data-reveal>
          <PhShieldCheck :size="22" weight="duotone" aria-hidden="true" />
          <h3>True Anonymity</h3>
          <p>We don't track your session or your identity. You are just a guest using a powerful tool.</p>
          <small>Secure by architecture</small>
        </article>

        <article class="home-page__feature home-page__feature--wide" data-reveal>
          <h3>Transparent &amp; Trusted</h3>
          <p>
            Our sanitisation logic is open for inspection. We use industry-standard regex and masking patterns to ensure
            your PII stays private.
          </p>
          <RouterLink to="/integrations" class="home-page__feature-link">
            Learn about our logic
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
        </article>
      </div>
    </section>

    <section class="home-page__final-cta" data-reveal>
      <h2>Ready to protect your<br />digital privacy?</h2>
      <p>Start using the tool immediately. No registration required, no strings attached.</p>

      <div class="home-page__final-actions">
        <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">Go to Sanitiser</RouterLink>
        <RouterLink class="btn btn--secondary" to="/integrations">How it works</RouterLink>
      </div>

      <small>Free to use • Private locally • No login</small>
    </section>
  </main>
</template>

<style scoped lang="scss">
.home-page {
  width: min(1200px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2rem;

  &__hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(340px, 0.7fr);
    gap: 2rem;
    align-items: stretch;
  }

  &__hero-copy {
    display: flex;
    flex-direction: column;
    height: 100%;

    h1 {
      margin: 1rem 0 0;
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(3.25rem, 7.8vw, 5.8rem);
      line-height: 0.94;
      letter-spacing: -0.05em;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 1.2rem 0 0;
      max-width: 34ch;
      color: var(--text-2);
      font-size: 1.08rem;
      line-height: 1.64;
    }
  }

  &__hero-tag {
    margin: 0;
    width: fit-content;
    border-radius: 999px;
    padding: 0.44rem 0.92rem;
    background: #d8f6e9;
    color: #247458;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 760;
  }

  &__hero-actions {
    margin-top: 1.45rem;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;

    .btn {
      min-height: 50px;
      padding-inline: 1.2rem;
    }
  }

  &__social-proof {
    margin-top: 1.5rem;
    display: inline-flex;
    align-items: center;
    gap: 0.8rem;

    p {
      margin: 0;
      font-size: 0.8rem;
      color: var(--text-3);
      max-width: none;
    }
  }

  &__avatars {
    display: inline-flex;

    span {
      width: 28px;
      height: 28px;
      border-radius: 999px;
      border: 2px solid color-mix(in srgb, var(--surface-0), white 10%);
      background: color-mix(in srgb, var(--accent-soft), var(--surface-0) 66%);
      color: var(--accent-3);
      display: grid;
      place-items: center;
      font-size: 0.7rem;
      font-weight: 760;
      margin-right: -8px;

      &:last-child {
        margin-right: 0;
      }
    }
  }

  &__hero-visual {
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    border-radius: 16px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    padding: 1.3rem 1.2rem 1.05rem;
    box-shadow: var(--shadow-sm);
    min-height: 0;
    height: 100%;
    display: grid;
    grid-template-rows: auto auto auto 1fr auto auto auto;
  }

  &__visual-eyebrow {
    margin: 0;
    text-align: right;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    font-weight: 760;
  }

  &__visual-block {
    border-radius: 10px;
    padding: 0.84rem 0.9rem;
    background: color-mix(in srgb, var(--surface-1), white 40%);
    min-height: 74px;

    small {
      display: block;
      margin-bottom: 0.44rem;
      font-size: 0.62rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-3);
      font-weight: 780;
    }

    code {
      display: block;
      font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.72rem;
      color: var(--text-3);
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }
  }

  &__visual-block--raw {
    margin-top: 0.92rem;
  }

  &__visual-block--safe {
    background: #e8f6ee;

    small,
    code {
      color: #1f6b4f;
    }
  }

  &__line {
    width: 1px;
    height: 54px;
    margin: 0.52rem auto;
  }

  &__line--blue {
    background: linear-gradient(180deg, transparent, #7da0ff, transparent);
  }

  &__line--green {
    background: linear-gradient(180deg, transparent, #80d8b0, transparent);
  }

  &__visual-shield {
    border-radius: 28px;
    background: linear-gradient(180deg, #2f64f7, #1851e6);
    color: white;
    padding: 1.5rem 1.2rem 1.1rem;
    display: grid;
    justify-items: center;
    align-content: center;
    min-height: 282px;
    gap: 0.5rem;
    box-shadow: 0 14px 28px color-mix(in srgb, #1851e6, transparent 66%);

    small {
      margin: 0;
      color: color-mix(in srgb, white, transparent 34%);
      font-size: 0.58rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-weight: 760;
    }

    strong {
      margin: 0;
      color: white;
      font-size: clamp(1.7rem, 2.5vw, 2.5rem);
      letter-spacing: -0.015em;
      font-weight: 780;
    }
  }

  &__shield-pulse {
    width: 90px;
    height: 90px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: color-mix(in srgb, white, transparent 88%);
    border: 1px solid color-mix(in srgb, white, transparent 70%);
    box-shadow: 0 0 0 0 color-mix(in srgb, white, transparent 76%);
    animation: homePulse 2.1s ease-out infinite;
  }

  &__shield-stream {
    margin-top: 0.46rem;
    width: min(300px, 84%);
    height: 8px;
    border-radius: 999px;
    background: color-mix(in srgb, white, transparent 80%);
    overflow: hidden;

    span {
      display: block;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, color-mix(in srgb, white, transparent 8%), color-mix(in srgb, white, transparent 30%));
      transition: width 420ms ease;
    }
  }

  &__shield-labels {
    width: min(300px, 84%);
    display: flex;
    justify-content: space-between;
    margin-top: 0.35rem;

    span {
      color: color-mix(in srgb, white, transparent 42%);
      font-size: 0.62rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 760;
    }
  }

  &__standard {
    margin-top: 4.2rem;
    padding-top: 3.2rem;
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
  }

  &__section-head {
    text-align: center;

    p {
      margin: 0;
      color: var(--accent-1);
      font-size: 0.68rem;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      font-weight: 760;
    }

    h2 {
      margin-top: 0.72rem;
      font-size: clamp(2.4rem, 4.5vw, 3.35rem);
      line-height: 1.03;
      letter-spacing: -0.04em;
    }
  }

  &__feature-grid {
    margin-top: 1.6rem;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.84rem;
  }

  &__feature {
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 26%);
    box-shadow: var(--shadow-xs);
    padding: 1.5rem;
    min-height: 212px;
    display: flex;
    flex-direction: column;

    svg {
      color: var(--text-2);
    }

    h3 {
      margin-top: 0.75rem;
      font-family: Manrope, Inter, sans-serif;
      font-size: 1.9rem;
      letter-spacing: -0.032em;
      line-height: 1.05;
    }

    p {
      margin: 0.72rem 0 0;
      font-size: 1rem;
      color: var(--text-2);
      line-height: 1.66;
      max-width: 44ch;
    }

    small {
      margin-top: auto;
      padding-top: 0.85rem;
      font-size: 0.64rem;
      color: var(--text-3);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 760;
    }
  }

  &__feature--wide {
    grid-column: span 2;
  }

  &__feature--accent {
    background: linear-gradient(180deg, #2457f5, #1347d8);
    color: white;

    svg,
    h3,
    p {
      color: inherit;
    }

    p {
      color: color-mix(in srgb, white, transparent 10%);
    }
  }

  &__chips {
    margin-top: auto;
    display: inline-flex;
    gap: 0.4rem;
    flex-wrap: wrap;

    span {
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-2), white 20%);
      color: var(--text-3);
      font-size: 0.62rem;
      font-weight: 720;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.28rem 0.55rem;
    }
  }

  &__feature-link {
    margin-top: auto;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    text-decoration: none;
    font-size: 0.88rem;
    color: var(--accent-1);
    font-weight: 730;
  }

  &__final-cta {
    margin: 3.4rem auto 0;
    border-radius: 26px;
    background: radial-gradient(circle at top, #071750, #020b33 70%);
    color: white;
    text-align: center;
    padding: clamp(2rem, 6vw, 3.5rem);
    width: min(1020px, 100%);

    h2 {
      font-size: clamp(2.2rem, 5vw, 3.6rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
      color: inherit;
    }

    p {
      margin: 1rem auto 0;
      max-width: 50ch;
      color: color-mix(in srgb, white, transparent 18%);
      font-size: 1rem;
      line-height: 1.64;
    }

    small {
      margin-top: 1.2rem;
      display: block;
      color: color-mix(in srgb, white, transparent 34%);
      font-size: 0.66rem;
      text-transform: uppercase;
      letter-spacing: 0.11em;
      font-weight: 760;
    }
  }

  &__final-actions {
    margin-top: 1.15rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.55rem;

    .btn {
      min-width: 164px;
      min-height: 50px;
    }

    .btn--secondary {
      background: transparent;
      border-color: color-mix(in srgb, white, transparent 76%);
      color: white;
    }
  }
}

[data-reveal] {
  opacity: 0;
  transform: translateY(18px);
  transition:
    opacity 560ms ease,
    transform 620ms cubic-bezier(0.22, 1, 0.36, 1);
  will-change: opacity, transform;
}

[data-reveal].is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 1040px) {
  .home-page {
    width: min(1200px, calc(100% - 1rem));

    &__hero {
      grid-template-columns: 1fr;
    }

    &__hero-visual {
      min-height: auto;
      padding: 1.1rem 1rem 1rem;
    }

    &__hero-copy p {
      max-width: none;
    }

    &__hero-copy {
      height: auto;
    }

    &__feature-grid {
      grid-template-columns: 1fr;
    }

    &__feature--wide {
      grid-column: auto;
    }
  }
}

@keyframes homePulse {
  0% {
    box-shadow: 0 0 0 0 color-mix(in srgb, white, transparent 76%);
  }
  70% {
    box-shadow: 0 0 0 16px color-mix(in srgb, white, transparent 100%);
  }
  100% {
    box-shadow: 0 0 0 0 color-mix(in srgb, white, transparent 100%);
  }
}
</style>
