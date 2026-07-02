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
        <p class="home-page__hero-tag">AI text anonymiser</p>
        <h1>
          SanitiseAI text anonymiser for sensitive documents.
        </h1>
        <p>
          Detect names, emails, IDs, secrets, addresses, and other sensitive details before text reaches AI tools,
          documents, or external workflows.
        </p>

        <div class="home-page__hero-actions">
          <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
            <span>Start sanitising</span>
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
          <RouterLink class="btn btn--secondary" to="/tool">Open tool</RouterLink>
        </div>

        <div class="home-page__social-proof">
          <span>Documents</span>
          <span>Prompts</span>
          <span>Logs</span>
          <span>Support notes</span>
        </div>
      </div>

      <article class="home-page__hero-visual" aria-label="Sanitisation flow preview" data-reveal>
        <p class="home-page__visual-eyebrow">Structured redaction</p>

        <div class="home-page__visual-block home-page__visual-block--raw">
          <small>Input source</small>
          <code>{ "user": "John Doe", "email": "john.doe@example.com", "ssn": "999-01-2234" }</code>
        </div>

        <div class="home-page__line home-page__line--blue"></div>

        <div class="home-page__visual-shield" aria-live="polite">
          <div class="home-page__shield-pulse" aria-hidden="true">
            <PhShieldCheck :size="18" weight="fill" aria-hidden="true" />
          </div>
          <small>Sanitiser active</small>
          <strong>Replacing sensitive values with readable tokens</strong>
          <div class="home-page__shield-stream" aria-hidden="true">
            <span style="width: 72%"></span>
          </div>
          <div class="home-page__shield-labels" aria-hidden="true">
            <span>Scanning</span>
            <span>Anonymising</span>
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
        <p>The SanitiseAI standard</p>
        <h2>Built around the actual sanitisation workflow.</h2>
      </header>

      <div class="home-page__feature-grid">
        <article class="home-page__feature home-page__feature--wide" data-reveal>
          <PhSparkle :size="24" weight="duotone" aria-hidden="true" />
          <h3>Detection that keeps context</h3>
          <p>
            The tool replaces sensitive values with consistent placeholders, so the text remains useful after
            sanitisation.
          </p>
          <div class="home-page__chips">
            <span>Immediate results</span>
            <span>Zero accounts</span>
          </div>
        </article>

        <article class="home-page__feature home-page__feature--accent" data-reveal>
          <PhLock :size="26" weight="fill" aria-hidden="true" />
          <h3>Fast first run</h3>
          <p>Open the tool, load an example, or paste your own content without going through a setup flow first.</p>
        </article>

        <article class="home-page__feature" data-reveal>
          <PhShieldCheck :size="22" weight="duotone" aria-hidden="true" />
          <h3>Clear handling</h3>
          <p>Text is sent to the sanitisation API over HTTPS for processing. Raw input is not stored by the tool.</p>
          <small>Privacy by design</small>
        </article>

        <article class="home-page__feature home-page__feature--wide" data-reveal>
          <h3>Customisable controls</h3>
          <p>
            Choose automatic mode for broad coverage or custom mode when you need precise control over entity types.
          </p>
          <RouterLink to="/integrations" class="home-page__feature-link">
            Explore integrations
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
        </article>
      </div>
    </section>

    <section class="home-page__faq" aria-labelledby="home-faq-title" data-reveal>
      <header class="home-page__section-head home-page__section-head--compact">
        <p>Common questions</p>
        <h2 id="home-faq-title">What SanitiseAI is built for.</h2>
      </header>

      <div class="home-page__faq-grid">
        <article data-reveal>
          <h3>What is SanitiseAI?</h3>
          <p>SanitiseAI is a text anonymiser for replacing sensitive information with readable placeholders before content is shared with AI tools, documents, or external workflows.</p>
        </article>
        <article data-reveal>
          <h3>What can it detect?</h3>
          <p>The sanitiser can detect common personal and operational identifiers including names, emails, phone numbers, addresses, dates, IDs, invoices, usernames, IP addresses, and secret keys.</p>
        </article>
        <article data-reveal>
          <h3>Who uses a PII redaction tool?</h3>
          <p>Teams use SanitiseAI for legal drafts, support tickets, medical notes, finance summaries, developer logs, contract excerpts, and prompt preparation.</p>
        </article>
        <article data-reveal>
          <h3>What happens to the output?</h3>
          <p>The output keeps the original structure where possible, replacing sensitive values with tokens such as [Person 1], [Email 1], or [Secret 1] so the text remains useful.</p>
        </article>
      </div>
    </section>

    <section class="home-page__final-cta" data-reveal>
      <h2>Ready to anonymise sensitive text?</h2>
      <p>Paste content, run detection, and copy structured output in one focused workflow.</p>

      <div class="home-page__final-actions">
        <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">Start sanitising</RouterLink>
        <RouterLink class="btn btn--secondary" to="/integrations">How it works</RouterLink>
      </div>

      <small>Structured placeholders • Focused browser workflow • Share-ready output</small>
    </section>
  </main>
</template>

<style scoped lang="scss">
.home-page {
    width: min(1180px, calc(100% - 2.4rem));
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
      max-width: 13ch;
      font-size: clamp(2.65rem, 6vw, 4.85rem);
      line-height: 1;
      letter-spacing: 0;

      span {
        color: var(--accent-1);
      }
    }

    p {
      margin: 1.2rem 0 0;
      max-width: 46ch;
      color: var(--text-2);
      font-size: 1.08rem;
      line-height: 1.64;
    }
  }

  &__hero-tag {
    margin: 0;
    width: fit-content;
    border-radius: var(--radius-sm);
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
    margin-top: 1.55rem;
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.42rem;
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 46%);
    padding-top: 0.95rem;

    span {
      margin: 0;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 24%);
      color: var(--text-2);
      font-size: 0.72rem;
      font-weight: 720;
      padding: 0.32rem 0.58rem;
    }
  }

  &__hero-visual {
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    border-radius: var(--radius-xl);
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
    border-radius: var(--radius-sm);
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
    border-radius: var(--radius-xl);
    background: linear-gradient(180deg, #2f64f7, #1851e6);
    color: white;
    padding: 1.5rem 1.2rem 1.1rem;
    display: grid;
    justify-items: center;
    align-content: center;
    min-height: 260px;
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
      text-align: center;
      font-size: clamp(1.25rem, 2vw, 1.8rem);
      line-height: 1.12;
      letter-spacing: 0;
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
      letter-spacing: 0;
    }
  }

  &__feature-grid {
    margin-top: 1.6rem;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.84rem;
  }

  &__feature {
    border-radius: var(--radius-lg);
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
      font-size: 1.7rem;
      letter-spacing: 0;
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

  &__faq {
    margin-top: 3.4rem;
    padding-top: 3rem;
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
  }

  &__section-head--compact {
    text-align: left;

    h2 {
      max-width: 11ch;
    }
  }

  &__faq-grid {
    margin-top: 1.45rem;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.84rem;

    article {
      border-radius: var(--radius-lg);
      background: color-mix(in srgb, var(--surface-0), var(--surface-1) 22%);
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 42%);
      padding: 1.15rem;
      min-height: 184px;
    }

    h3 {
      margin: 0;
      color: var(--text-1);
      font-size: 1rem;
      line-height: 1.24;
      letter-spacing: 0;
    }

    p {
      margin: 0.68rem 0 0;
      color: var(--text-2);
      font-size: 0.9rem;
      line-height: 1.58;
    }
  }

  &__final-cta {
    margin: 3.4rem auto 0;
    border-radius: var(--radius-xl);
    background: linear-gradient(180deg, #102a6b, #071944);
    color: white;
    text-align: center;
    padding: clamp(2rem, 6vw, 3.5rem);
    width: min(1020px, 100%);

    h2 {
      font-size: clamp(2.2rem, 5vw, 3.6rem);
      line-height: 1;
      letter-spacing: 0;
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

    &__feature-grid,
    &__faq-grid {
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
