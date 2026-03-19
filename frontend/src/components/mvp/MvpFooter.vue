<template>
  <footer class="mvp-footer">
    <div class="mvp-footer__inner">
      <div class="mvp-footer__brand">
        <strong>SanitiseAI</strong>
        <p>Built for safe-to-share text across AI prompts, contracts, and notes.</p>
      </div>

      <nav class="mvp-footer__links" aria-label="Footer links">
        <a href="/privacy.html">Privacy policy</a>
        <a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">GitHub</a>
        <a href="mailto:nimaparsi@icloud.com">Contact</a>
      </nav>
    </div>

    <p class="mvp-footer__meta">No data stored • Instant processing • Privacy-first</p>
  </footer>
</template>

<style scoped lang="scss">
.mvp-footer {
  margin-top: 4.6rem;
  padding: 1.4rem 0 2rem;
  border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);

  &__inner {
    width: min(1200px, calc(100% - 2.8rem));
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  &__brand {
    strong {
      font-family: 'Space Grotesk', Manrope, sans-serif;
      font-size: 1rem;
      letter-spacing: -0.02em;
      color: var(--text-1);
    }

    p {
      margin: 0.4rem 0 0;
      max-width: 44ch;
      font-size: 0.88rem;
      color: var(--text-3);
      line-height: 1.6;
    }
  }

  &__links {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;

    a {
      text-decoration: none;
      color: var(--text-2);
      font-size: 0.88rem;
      font-weight: 600;
      transition: color 180ms ease;

      &:hover,
      &:focus-visible {
        color: var(--accent-1);
      }
    }
  }

  &__meta {
    width: min(1200px, calc(100% - 2.8rem));
    margin: 1rem auto 0;
    font-size: 0.8rem;
    color: var(--text-3);
  }
}

@media (max-width: 980px) {
  .mvp-footer {
    margin-top: 3rem;

    &__inner,
    &__meta {
      width: min(1200px, calc(100% - 1.2rem));
    }

    &__inner {
      flex-direction: column;
      gap: 0.9rem;
    }
  }
}
</style>
