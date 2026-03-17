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
    background:
      radial-gradient(300px 160px at 20% 0%, rgba(37, 99, 235, 0.12) 0%, transparent 62%),
      #ffffff;
  }

  &__copy {
    background: #ffffff;
  }

  &__browser {
    border: 1px solid #dbe4f5;
    border-radius: 22px;
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
    padding: 1.05rem;
  }

  &__eyebrow {
    margin: 0;
    color: #1d4ed8;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h2 {
    margin: 0.5rem 0 0;
    color: #0f172a;
    font-size: clamp(1.35rem, 3.3vw, 1.95rem);
    letter-spacing: -0.02em;
    line-height: 1.2;
  }

  p {
    margin: 0.72rem 0 0;
    color: #475569;
    line-height: 1.55;
  }

  &__works-inside {
    margin-top: 1rem;

    p {
      margin: 0;
      font-size: 0.85rem;
      color: #334155;
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
      border: 1px solid #d6e2f7;
      background: #f8fbff;
      color: #1e293b;
      border-radius: 999px;
      padding: 0.3rem 0.58rem;
      font-size: 0.82rem;
      font-weight: 600;
    }
  }

  &__cta {
    margin-top: 1rem;
    border: 0;
    border-radius: 12px;
    background: linear-gradient(145deg, #2563eb, #4338ca);
    color: #ffffff;
    font-size: 0.9rem;
    font-weight: 700;
    padding: 0.62rem 0.96rem;
    cursor: pointer;
    box-shadow: 0 10px 24px rgba(59, 130, 246, 0.3);
    transition: transform 160ms ease, box-shadow 180ms ease;

    &:hover,
    &:focus-visible {
      transform: translateY(-1px);
      box-shadow: 0 14px 28px rgba(59, 130, 246, 0.36);
    }
  }

  &__notice {
    margin: 0.6rem 0 0;
    color: #1d4ed8;
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
      background: #bfdbfe;
    }
  }

  &__preview {
    margin-top: 0.72rem;
    border: 1px solid #1f2937;
    border-radius: 15px;
    background:
      linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.96)),
      #0b1220;
    padding: 0.85rem;
    color: #e2e8f0;

    button {
      margin-top: 0.75rem;
      width: 100%;
      border: 1px solid #22c55e;
      border-radius: 11px;
      background: rgba(34, 197, 94, 0.15);
      color: #bbf7d0;
      font-size: 0.85rem;
      font-weight: 700;
      padding: 0.56rem;
      cursor: pointer;
      transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;

      &:hover,
      &:focus-visible {
        background: rgba(34, 197, 94, 0.24);
        border-color: #4ade80;
        transform: translateY(-1px);
      }
    }
  }

  &__preview-title {
    margin: 0;
    color: #f8fafc;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.01em;
  }

  &__preview-chat {
    margin-top: 0.58rem;
    border: 1px solid rgba(71, 85, 105, 0.65);
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.75);
    padding: 0.58rem 0.64rem;
    color: #cbd5e1;
    font-size: 0.84rem;
    line-height: 1.5;

    span {
      color: #86efac;
      font-weight: 700;
    }
  }

  &__preview-detected {
    margin-top: 0.62rem;
    border: 1px solid rgba(71, 85, 105, 0.65);
    border-radius: 12px;
    background: rgba(2, 6, 23, 0.64);
    padding: 0.54rem 0.6rem;

    p {
      margin: 0;
      font-size: 0.83rem;
      color: #94a3b8;
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
      border: 1px solid rgba(51, 65, 85, 0.72);
      border-radius: 10px;
      padding: 0.38rem 0.5rem;
      background: rgba(15, 23, 42, 0.74);
      color: #cbd5e1;
      font-size: 0.83rem;

      strong {
        color: #86efac;
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
