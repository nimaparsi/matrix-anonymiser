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
    border: 1px solid rgba(67, 56, 202, 0.35);
    border-radius: 14px;
    background: linear-gradient(145deg, #4f46e5, #2563eb);
    color: #ffffff;
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    padding: 0.68rem 1.06rem;
    cursor: pointer;
    box-shadow: 0 12px 28px rgba(59, 130, 246, 0.34);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 18px 34px rgba(59, 130, 246, 0.42);
    }
  }
}

</style>
