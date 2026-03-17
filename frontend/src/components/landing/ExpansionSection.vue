<script setup lang="ts">
import { onUnmounted, ref } from 'vue'

const integrations = ['ChatGPT', 'Claude', 'Gemini', 'Google Docs', 'Gmail']
const notice = ref('')
let noticeTimer: ReturnType<typeof window.setTimeout> | null = null

function showComingSoon() {
  notice.value = 'Chrome extension beta is opening soon.'
  if (noticeTimer) window.clearTimeout(noticeTimer)
  noticeTimer = window.setTimeout(() => {
    notice.value = ''
    noticeTimer = null
  }, 2200)
}

onUnmounted(() => {
  if (noticeTimer) {
    window.clearTimeout(noticeTimer)
    noticeTimer = null
  }
})
</script>

<template>
  <section class="expansion" aria-labelledby="expansion-title">
    <div class="expansion__grid">
      <div class="expansion__copy">
        <p class="expansion__eyebrow">Product expansion</p>
        <h2 id="expansion-title">Bring SanitiseAI directly into your workflow</h2>
        <p>Use a lightweight browser extension to sanitise prompts before they leave your tab.</p>

        <div class="expansion__works-inside">
          <p>Works inside</p>
          <ul>
            <li v-for="item in integrations" :key="item">{{ item }}</li>
          </ul>
        </div>

        <button type="button" class="expansion__cta" @click="showComingSoon">Get Chrome extension</button>
        <p v-if="notice" class="expansion__notice" role="status" aria-live="polite">{{ notice }}</p>
      </div>

      <article class="expansion__browser" aria-label="Browser extension preview">
        <div class="expansion__browser-top">
          <span></span><span></span><span></span>
        </div>
        <div class="expansion__preview">
          <p class="expansion__preview-title">Sanitise before send</p>
          <div class="expansion__preview-chat">
            Hi, this is <span>[Person 1]</span> from <span>[Organisation 1]</span>. Email me at <span>[Email 1]</span> or call <span>[Phone 1]</span>.
          </div>
          <div class="expansion__preview-detected">
            <p>Detected</p>
            <ul>
              <li><span>Person</span><strong>x 2</strong></li>
              <li><span>Email</span><strong>x 1</strong></li>
              <li><span>Phone</span><strong>x 1</strong></li>
            </ul>
          </div>
          <button type="button" @click="showComingSoon">Apply anonymisation</button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.expansion {
  &__grid {
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
    gap: 1rem;
    align-items: stretch;
  }

  &__copy,
  &__browser {
    background: color-mix(in srgb, var(--surface-glass), transparent 4%);
    border: 1px solid var(--border-1);
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(14px);
  }

  &__copy {
    border-radius: 22px;
    padding: 1.05rem;
  }

  &__browser {
    border-radius: 22px;
    padding: 1.05rem;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h2 {
    margin: 0.5rem 0 0;
    color: var(--text-1);
    font-size: clamp(1.35rem, 3.3vw, 1.95rem);
    letter-spacing: -0.02em;
    line-height: 1.2;
  }

  p {
    margin: 0.72rem 0 0;
    color: var(--text-2);
    line-height: 1.55;
  }

  &__works-inside {
    margin-top: 1rem;

    p {
      margin: 0;
      font-size: 0.85rem;
      color: var(--text-2);
      font-weight: 700;
    }

    ul {
      list-style: none;
      margin: 0.5rem 0 0;
      padding: 0;
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
    }

    li {
      border: 1px solid var(--border-1);
      background: color-mix(in srgb, var(--surface-1), transparent 3%);
      color: var(--text-1);
      border-radius: 999px;
      padding: 0.3rem 0.58rem;
      font-size: 0.82rem;
      font-weight: 600;
    }
  }

  &__cta {
    margin-top: 1rem;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 46%);
    border-radius: 12px;
    background: linear-gradient(145deg, var(--accent-1), var(--accent-2));
    color: var(--accent-ink);
    font-size: 0.9rem;
    font-weight: 700;
    padding: 0.62rem 0.96rem;
    cursor: pointer;
    box-shadow:
      0 10px 24px color-mix(in srgb, var(--accent-2), transparent 67%),
      inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 88%);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow:
        0 14px 28px color-mix(in srgb, var(--accent-2), transparent 60%),
        inset 0 -8px 14px color-mix(in srgb, var(--accent-1), #000 86%);
    }
  }

  &__notice {
    margin: 0.6rem 0 0;
    color: var(--accent-2);
    font-size: 0.82rem;
    font-weight: 600;
  }

  &__browser-top {
    display: flex;
    align-items: center;
    gap: 0.38rem;

    span {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent-2), transparent 40%);
    }
  }

  &__preview {
    margin-top: 0.72rem;
    border: 1px solid color-mix(in srgb, var(--accent-2), transparent 72%);
    border-radius: 15px;
    background:
      linear-gradient(
        180deg,
        color-mix(in srgb, var(--surface-1), #000 26%),
        color-mix(in srgb, var(--surface-0), #000 35%)
      );
    padding: 0.85rem;
    color: var(--text-2);

    button {
      margin-top: 0.75rem;
      width: 100%;
      border: 1px solid color-mix(in srgb, var(--accent-1), transparent 36%);
      border-radius: 11px;
      background: color-mix(in srgb, var(--accent-1), transparent 84%);
      color: color-mix(in srgb, var(--accent-1), white 30%);
      font-size: 0.85rem;
      font-weight: 700;
      padding: 0.56rem;
      cursor: pointer;
      transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;

      &:hover,
      &:focus-visible {
        background: color-mix(in srgb, var(--accent-1), transparent 76%);
        border-color: color-mix(in srgb, var(--accent-1), transparent 24%);
        transform: translateY(-1px);
      }
    }
  }

  &__preview-title {
    margin: 0;
    color: var(--text-1);
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.01em;
  }

  &__preview-chat {
    margin-top: 0.58rem;
    border: 1px solid var(--border-1);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), #000 18%);
    padding: 0.58rem 0.64rem;
    color: var(--text-2);
    font-size: 0.84rem;
    line-height: 1.5;

    span {
      color: var(--accent-1);
      font-weight: 700;
    }
  }

  &__preview-detected {
    margin-top: 0.62rem;
    border: 1px solid var(--border-1);
    border-radius: 12px;
    background: color-mix(in srgb, var(--surface-0), #000 22%);
    padding: 0.54rem 0.6rem;

    p {
      margin: 0;
      font-size: 0.83rem;
      color: var(--text-3);
      font-weight: 700;
    }

    ul {
      margin: 0.42rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.34rem;
    }

    li {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.72rem;
      border: 1px solid var(--border-1);
      border-radius: 10px;
      padding: 0.38rem 0.5rem;
      background: color-mix(in srgb, var(--surface-0), #000 15%);
      color: var(--text-2);
      font-size: 0.83rem;

      strong {
        color: var(--accent-1);
        font-weight: 800;
      }
    }
  }
}

@media (max-width: 980px) {
  .expansion {
    &__grid {
      grid-template-columns: 1fr;
    }
  }
}

</style>
