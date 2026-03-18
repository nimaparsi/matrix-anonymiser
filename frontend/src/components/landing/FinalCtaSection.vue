<script setup lang="ts">
import { PhSparkle } from '@phosphor-icons/vue'

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
    min-height: 46px;
    border-radius: 14px;
    padding-inline: 1.06rem;
  }
}
</style>
