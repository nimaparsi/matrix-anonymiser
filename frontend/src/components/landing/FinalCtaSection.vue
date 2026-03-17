<script setup lang="ts">
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
  }, 140)
}
</script>

<template>
  <section class="final-cta" aria-labelledby="final-cta-title">
    <div class="final-cta__box">
      <h2 id="final-cta-title">Ready to sanitise sensitive text?</h2>
      <p>Turn names, emails, phone numbers and more into safe-to-share text in seconds.</p>
      <button class="final-cta__btn" type="button" @click="runTryItFree">Try it free</button>
    </div>
  </section>
</template>

<style scoped lang="scss">
.final-cta {
  &__box {
    border-radius: 22px;
    border: 1px solid var(--border-1);
    background:
      radial-gradient(
        760px 240px at 10% 0%,
        color-mix(in srgb, var(--accent-2), transparent 82%) 0%,
        transparent 55%
      ),
      color-mix(in srgb, var(--surface-glass), transparent 3%);
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(12px);
    padding: 1.2rem;
    text-align: center;

    h2 {
      margin: 0;
      color: var(--text-1);
      font-size: clamp(1.45rem, 3.8vw, 2.1rem);
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.65rem auto 0;
      color: var(--text-2);
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
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 44%);
    border-radius: 14px;
    background: linear-gradient(145deg, var(--accent-1), var(--accent-2));
    color: var(--accent-ink);
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    padding: 0.68rem 1.06rem;
    cursor: pointer;
    box-shadow:
      0 12px 28px color-mix(in srgb, var(--accent-2), transparent 66%),
      inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 88%);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow:
        0 18px 34px color-mix(in srgb, var(--accent-2), transparent 58%),
        inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 86%);
    }
  }
}

</style>
