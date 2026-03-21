<template>
  <footer class="mvp-footer">
    <div class="mvp-footer__inner">
      <div class="mvp-footer__brand">
        <strong>SanitiseAI</strong>
        <p>© 2026 SanitiseAI. Privacy by design.</p>
      </div>

      <nav class="mvp-footer__links" aria-label="Footer links">
        <a href="/terms.html">Terms</a>
        <a href="/privacy.html">Privacy policy</a>
        <a href="mailto:nimaparsi@icloud.com">Contact</a>
      </nav>
    </div>
  </footer>
</template>

<style scoped lang="scss">
.mvp-footer {
  margin-top: 4rem;
  padding: 2rem 0 1.6rem;
  border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 42%);
  background: color-mix(in srgb, var(--surface-1), white 6%);

  &__inner {
    width: min(1200px, calc(100% - 2.4rem));
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.9rem;
  }

  &__brand {
    strong {
      font-family: Manrope, Inter, sans-serif;
      font-size: 1.02rem;
      letter-spacing: -0.03em;
      color: var(--text-1);
      font-weight: 780;
    }

    p {
      margin: 0.35rem 0 0;
      max-width: 44ch;
      font-size: 0.74rem;
      color: var(--text-3);
      line-height: 1.5;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 680;
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
      font-size: 0.72rem;
      font-weight: 650;
      text-transform: uppercase;
      letter-spacing: 0.09em;
      transition: color 180ms ease, opacity 180ms ease;
      opacity: 0.9;

      &:hover,
      &:focus-visible {
        color: var(--accent-1);
        opacity: 1;
      }
    }
  }
}

@media (max-width: 980px) {
  .mvp-footer {
    margin-top: 2.6rem;

    &__inner {
      width: min(1200px, calc(100% - 1rem));
    }

    &__inner {
      flex-direction: column;
      gap: 0.9rem;
    }
  }
}
</style>
