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
  border-top: 1px solid #dce6f8;

  &__inner {
    display: grid;
    gap: 0.28rem;
    color: #64748b;
    font-size: 0.92rem;
    line-height: 1.45;

    p {
      margin: 0;
    }

    a {
      width: fit-content;
      color: #334155;
      text-decoration: none;
      border-bottom: 1px solid rgba(51, 65, 85, 0.36);
      transition: color 160ms ease, border-color 160ms ease;
    }

    a:hover,
    a:focus-visible {
      color: #1d4ed8;
      border-color: rgba(37, 99, 235, 0.5);
    }
  }
}
</style>
