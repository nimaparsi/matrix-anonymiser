<script setup lang="ts">
const integrations = ['ChatGPT', 'Claude', 'Gemini', 'Google Docs', 'Gmail']
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

        <button type="button" class="expansion__cta">Get Chrome extension</button>
      </div>

      <article class="expansion__browser" aria-label="Browser extension preview">
        <div class="expansion__browser-top">
          <span></span><span></span><span></span>
        </div>
        <div class="expansion__browser-body">
          <h3>Sanitise before send</h3>
          <p>Detected</p>
          <ul>
            <li>Person x 2</li>
            <li>Email x 1</li>
            <li>Phone x 1</li>
          </ul>
          <button type="button">Apply anonymisation</button>
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
    border: 1px solid #dbe4f5;
    border-radius: 22px;
    background: #ffffff;
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

  &__browser-body {
    margin-top: 0.72rem;
    border: 1px solid #d9e3f7;
    border-radius: 15px;
    background: #f8fbff;
    padding: 0.85rem;

    h3 {
      margin: 0;
      color: #0f172a;
      font-size: 1rem;
    }

    p {
      margin: 0.52rem 0 0;
      font-size: 0.84rem;
      color: #475569;
    }

    ul {
      margin: 0.35rem 0 0;
      padding-left: 1rem;
      color: #1e293b;
      font-size: 0.86rem;
      line-height: 1.5;
    }

    button {
      margin-top: 0.75rem;
      width: 100%;
      border: 1px solid #bfdbfe;
      border-radius: 10px;
      background: #ffffff;
      color: #1d4ed8;
      font-size: 0.85rem;
      font-weight: 700;
      padding: 0.52rem;
      cursor: pointer;
      transition: background 160ms ease, border-color 160ms ease;

      &:hover,
      &:focus-visible {
        background: #eff6ff;
        border-color: #93c5fd;
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
