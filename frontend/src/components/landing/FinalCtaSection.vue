<script setup lang="ts">
import { PhSparkle } from '@phosphor-icons/vue'

const QUICK_START_TEXT = 'John Smith from Acme emailed john@acme.com\nCall me on 07912345678'

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
  <section class="final-cta" aria-labelledby="final-cta-title">
    <div class="final-cta__box">
      <h2 id="final-cta-title">Ready to sanitise sensitive text?</h2>
      <p>Try SanitiseAI free and see how quickly names, emails, phone numbers and more can be made safe to share.</p>
      <button class="btn btn--primary final-cta__btn" type="button" @click="runTryItFree">
        <PhSparkle :size="16" weight="fill" aria-hidden="true" />
        <span>Try it free</span>
      </button>
    </div>
  </section>
</template>

<style scoped lang="scss">
.final-cta {
  &__box {
    border-radius: 20px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
    background:
      radial-gradient(130% 110% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 68%), transparent 52%),
      var(--surface-0);
    box-shadow: var(--shadow-md);
    padding: clamp(1.2rem, 3vw, 1.8rem);
    text-align: center;

    h2 {
      margin: 0;
      font-size: clamp(1.8rem, 3.6vw, 2.4rem);
      line-height: 1.06;
      letter-spacing: -0.03em;
    }

    p {
      margin: 0.72rem auto 0;
      max-width: 56ch;
      color: var(--text-2);
      font-size: 1rem;
      line-height: 1.6;
    }
  }

  &__btn {
    margin-top: 1rem;
    min-height: 48px;
    padding-inline: 1.14rem;
  }
}
</style>
