<template>
  <section class="final-cta" aria-labelledby="final-cta-title">
    <div class="final-cta__box">
      <h2 id="final-cta-title">Ready to sanitise your first prompt?</h2>
      <p>Try SanitiseAI free and see how quickly sensitive text can be made safe-to-share.</p>
      <a href="#demo" class="final-cta__btn">Try it free</a>
    </div>
  </section>
</template>

<style scoped lang="scss">
.final-cta {
  &__box {
    border-radius: 22px;
    border: 1px solid rgba(99, 102, 241, 0.24);
    background:
      radial-gradient(760px 240px at 10% 0%, rgba(96, 165, 250, 0.14) 0%, transparent 55%),
      #ffffff;
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
    padding: 1.2rem;
    text-align: center;

    h2 {
      margin: 0;
      color: #0f172a;
      font-size: clamp(1.45rem, 3.8vw, 2.1rem);
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.65rem auto 0;
      color: #475569;
      font-size: 1rem;
      line-height: 1.55;
      max-width: 56ch;
    }
  }

  &__btn {
    margin-top: 1rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: 12px;
    background: linear-gradient(145deg, #2563eb, #4338ca);
    color: #ffffff;
    font-size: 0.95rem;
    font-weight: 700;
    padding: 0.66rem 1rem;
    cursor: pointer;
    text-decoration: none;
    box-shadow: 0 12px 26px rgba(59, 130, 246, 0.32);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 16px 30px rgba(59, 130, 246, 0.38);
    }
  }
}

</style>
