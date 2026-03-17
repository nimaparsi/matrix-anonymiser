<template>
  <footer class="landing-footer" aria-label="Site footer">
    <div class="landing-footer__inner">
      <p>Built by Nima Parsi</p>
      <a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">Open source on GitHub</a>
      <a href="/privacy.html">Privacy policy</a>
      <p>No data stored</p>
      <p>Sensitive data is anonymised before any AI processing.</p>
      <p>Powered by the Matrix Privacy Engine</p>
    </div>
  </footer>
</template>

<style scoped lang="scss">
.landing-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-1);

  &__inner {
    display: grid;
    gap: 0.28rem;
    color: var(--text-3);
    font-size: 0.92rem;
    line-height: 1.45;

    p {
      margin: 0;
    }

    a {
      width: fit-content;
      color: var(--text-2);
      text-decoration: none;
      border-bottom: 1px solid color-mix(in srgb, var(--text-2), transparent 58%);
      transition: color 160ms ease, border-color 160ms ease;
    }

    a:hover,
    a:focus-visible {
      color: var(--accent-2);
      border-color: color-mix(in srgb, var(--accent-2), transparent 46%);
    }
  }
}
</style>
