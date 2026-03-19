<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhCheckCircle, PhShieldCheck, PhSparkle, PhUploadSimple } from '@phosphor-icons/vue'

const featureCards = [
  {
    title: 'Detect sensitive entities',
    body: 'Find names, emails, phone numbers, addresses, invoice IDs, IP addresses, secrets, and usernames in seconds.',
  },
  {
    title: 'Sanitise before sharing',
    body: 'Replace sensitive values with structured placeholders so the text remains useful for AI tools and collaborators.',
  },
  {
    title: 'Privacy-first workflow',
    body: 'Run the core sanitisation flow instantly with no account wall: paste, sanitise, copy, export.',
  },
]

const trustItems = ['No login required', 'No data storage', 'Instant processing', 'Built for contracts, notes, prompts']
</script>

<template>
  <main class="home">
    <section class="home__hero">
      <div class="home__hero-copy">
        <p class="home__eyebrow">SanitiseAI MVP</p>
        <h1>Protect your data without compromise.</h1>
        <p class="home__lede">
          SanitiseAI anonymises sensitive text before it reaches AI tools, documents, and team workflows. Turn raw content
          into safe-to-share output in one pass.
        </p>

        <div class="home__cta-row">
          <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
            <PhSparkle :size="16" weight="fill" aria-hidden="true" />
            <span>Start sanitising</span>
          </RouterLink>
          <RouterLink class="btn btn--secondary" to="/integrations">
            <PhUploadSimple :size="16" weight="duotone" aria-hidden="true" />
            <span>View integrations</span>
          </RouterLink>
        </div>

        <ul class="home__trust-list">
          <li v-for="item in trustItems" :key="item">
            <PhCheckCircle :size="14" weight="fill" aria-hidden="true" />
            <span>{{ item }}</span>
          </li>
        </ul>
      </div>

      <article class="home__hero-demo" aria-label="Transformation preview">
        <header>
          <p>Live workflow preview</p>
          <span>input → sanitised output</span>
        </header>

        <div class="home__preview-grid">
          <div class="home__preview-panel">
            <h3>Original text</h3>
            <p>John Smith from Acme emailed john@acme.com</p>
            <p>Call me on 07912345678</p>
          </div>

          <div class="home__preview-panel home__preview-panel--output">
            <h3>Sanitised output</h3>
            <p>
              <span class="token token--person">[Person 1]</span>
              from
              <span class="token token--organisation">[Organisation 1]</span>
              emailed
              <span class="token token--email">[Email 1]</span>
            </p>
            <p>
              Call me on
              <span class="token token--phone">[Phone 1]</span>
            </p>
          </div>
        </div>

        <RouterLink class="home__preview-link" :to="{ path: '/tool', query: { demo: '1' } }">
          Try it free in the tool
          <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
        </RouterLink>
      </article>
    </section>

    <section class="home__compat" aria-label="Compatible tools">
      <p>Compatible with</p>
      <ul>
        <li><img src="/brands/openai.svg" alt="ChatGPT" />ChatGPT</li>
        <li><img src="/brands/claude.svg" alt="Claude" />Claude</li>
        <li><img src="/brands/gemini.svg" alt="Gemini" />Gemini</li>
        <li><img src="/brands/gmail.svg" alt="Email" />Email</li>
        <li><img src="/brands/googledocs.svg" alt="Docs" />Docs</li>
      </ul>
    </section>

    <section class="home__features">
      <header>
        <p class="home__eyebrow">Why SanitiseAI</p>
        <h2>A focused privacy layer for sensitive text</h2>
      </header>

      <div class="home__feature-grid">
        <article v-for="card in featureCards" :key="card.title">
          <PhShieldCheck :size="20" weight="duotone" aria-hidden="true" />
          <h3>{{ card.title }}</h3>
          <p>{{ card.body }}</p>
        </article>
      </div>
    </section>

    <section class="home__cta-final">
      <h2>Ready to sanitise sensitive text?</h2>
      <p>Use the tool now and get safe-to-share output in seconds. No signup required.</p>
      <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
        <PhSparkle :size="16" weight="fill" aria-hidden="true" />
        <span>Try it free</span>
      </RouterLink>
    </section>
  </main>
</template>

<style scoped lang="scss">
.home {
  width: min(1200px, calc(100% - 2.8rem));
  margin: 0 auto;
  padding-top: 2.1rem;

  &__hero {
    display: grid;
    grid-template-columns: 1.04fr 0.96fr;
    gap: 1.4rem;
    align-items: start;
  }

  &__hero-copy {
    h1 {
      margin-top: 0.72rem;
      font-size: clamp(2.5rem, 6vw, 4.5rem);
      line-height: 0.93;
      letter-spacing: -0.04em;
      max-width: 12ch;
    }
  }

  &__eyebrow {
    margin: 0;
    font-size: 0.77rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--accent-1);
    font-weight: 780;
  }

  &__lede {
    margin: 1rem 0 0;
    max-width: 56ch;
    font-size: 1.05rem;
    line-height: 1.65;
    color: var(--text-2);
  }

  &__cta-row {
    margin-top: 1.2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;

    .btn {
      min-height: 48px;
    }
  }

  &__trust-list {
    margin: 1.1rem 0 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 0.48rem;

    li {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-1), var(--accent-soft) 18%);
      padding: 0.34rem 0.62rem;
      font-size: 0.78rem;
      color: var(--text-2);
      font-weight: 650;

      svg {
        color: var(--accent-1);
      }
    }
  }

  &__hero-demo {
    border-radius: 20px;
    background: var(--surface-0);
    box-shadow: var(--shadow-lg);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 60%);
    padding: 1rem;

    header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 0.6rem;

      p {
        margin: 0;
        font-weight: 780;
        color: var(--text-1);
        font-size: 0.95rem;
      }

      span {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-3);
        font-weight: 700;
      }
    }
  }

  &__preview-grid {
    margin-top: 0.86rem;
    display: grid;
    gap: 0.68rem;
  }

  &__preview-panel {
    border-radius: 14px;
    background: color-mix(in srgb, var(--surface-1), white 20%);
    padding: 0.8rem;

    h3 {
      margin: 0;
      color: var(--text-2);
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    p {
      margin: 0.45rem 0 0;
      color: var(--text-2);
      line-height: 1.58;
      font-size: 0.93rem;
    }
  }

  &__preview-panel--output {
    background: color-mix(in srgb, var(--accent-soft), white 62%);

    p {
      color: var(--text-1);
    }
  }

  &__preview-link {
    margin-top: 0.82rem;
    width: fit-content;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    text-decoration: none;
    font-weight: 700;
    color: var(--accent-1);
    font-size: 0.88rem;
  }

  &__compat {
    margin-top: 2.2rem;
    border-radius: 16px;
    background: color-mix(in srgb, var(--surface-0), white 16%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 52%);
    box-shadow: var(--shadow-sm);
    padding: 0.88rem 1rem;

    p {
      margin: 0;
      font-size: 0.76rem;
      color: var(--text-3);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 760;
    }

    ul {
      margin: 0.6rem 0 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.48rem;

      li {
        border-radius: 999px;
        background: var(--surface-0);
        border: 1px solid color-mix(in srgb, var(--border-1), transparent 52%);
        padding: 0.36rem 0.62rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.8rem;
        color: var(--text-2);
        font-weight: 650;

        img {
          width: 17px;
          height: 17px;
          display: block;
        }
      }
    }
  }

  &__features {
    margin-top: 3.2rem;

    h2 {
      margin-top: 0.55rem;
      font-size: clamp(1.9rem, 4vw, 2.7rem);
      line-height: 1.06;
      max-width: 16ch;
    }
  }

  &__feature-grid {
    margin-top: 1.1rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;

    article {
      border-radius: 16px;
      background: var(--surface-0);
      box-shadow: var(--shadow-sm);
      padding: 1rem;
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 56%);

      svg {
        color: var(--accent-1);
      }

      h3 {
        margin: 0.56rem 0 0;
        font-size: 1rem;
      }

      p {
        margin: 0.44rem 0 0;
        color: var(--text-2);
        line-height: 1.58;
        font-size: 0.9rem;
      }
    }
  }

  &__cta-final {
    margin-top: 3.6rem;
    border-radius: 22px;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    color: white;
    padding: clamp(1.4rem, 4vw, 2.1rem);
    text-align: center;
    box-shadow: 0 24px 48px color-mix(in srgb, var(--accent-1), transparent 70%);

    h2 {
      font-size: clamp(1.8rem, 3.8vw, 2.7rem);
      line-height: 1.05;
      letter-spacing: -0.03em;
      color: inherit;
    }

    p {
      margin: 0.74rem auto 0;
      max-width: 56ch;
      color: color-mix(in srgb, white, transparent 14%);
      font-size: 0.98rem;
      line-height: 1.6;
    }

    .btn {
      margin-top: 1rem;
      min-height: 48px;
      border-color: color-mix(in srgb, white, transparent 20%);
      background: white;
      color: var(--accent-3);
      box-shadow: none;
    }
  }
}

.token {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 0.12rem 0.5rem;
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  font-weight: 700;
  margin: 0.04rem 0.1rem;
}

.token--person {
  background: color-mix(in srgb, #dbeafe, white 30%);
  border-color: color-mix(in srgb, #3b82f6, transparent 46%);
  color: color-mix(in srgb, #1d4ed8, black 14%);
}

.token--organisation {
  background: color-mix(in srgb, #e9d5ff, white 34%);
  border-color: color-mix(in srgb, #8b5cf6, transparent 48%);
  color: color-mix(in srgb, #6d28d9, black 14%);
}

.token--email {
  background: color-mix(in srgb, #dbeafe, white 38%);
  border-color: color-mix(in srgb, #2563eb, transparent 48%);
  color: color-mix(in srgb, #1e40af, black 10%);
}

.token--phone {
  background: color-mix(in srgb, #cffafe, white 36%);
  border-color: color-mix(in srgb, #0891b2, transparent 48%);
  color: color-mix(in srgb, #155e75, black 10%);
}

@media (max-width: 980px) {
  .home {
    width: min(1200px, calc(100% - 1.2rem));

    &__hero {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    &__hero-copy h1 {
      max-width: none;
    }

    &__feature-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
