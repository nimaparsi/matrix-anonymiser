<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { PhArrowRight, PhBrowser, PhCode, PhDeviceMobile, PhPlugsConnected, PhRocketLaunch } from '@phosphor-icons/vue'

const cards = [
  {
    title: 'Chrome & Edge extension',
    description: 'Sanitise sensitive text directly inside AI chat and browser-based workflows before sharing.',
    status: 'Testing beta',
    icon: PhBrowser,
  },
  {
    title: 'API integration',
    description: 'Embed sanitisation into internal systems and prompt pipelines with lightweight HTTP requests.',
    status: 'Early access',
    icon: PhCode,
  },
  {
    title: 'iOS app',
    description: 'Use share-sheet style sanitisation on mobile before sending text to AI tools and messaging apps.',
    status: 'Planned',
    icon: PhDeviceMobile,
  },
]

const roadmap = [
  { title: 'VS Code helper', tag: 'Coming soon' },
  { title: 'Google Workspace add-on', tag: 'Coming soon' },
  { title: 'Slack command', tag: 'Researching' },
  { title: 'Notion integration', tag: 'Researching' },
]
</script>

<template>
  <main class="integrations">
    <section class="integrations__hero">
      <p class="integrations__eyebrow">Integrations (MVP)</p>
      <h1>Your privacy everywhere you work.</h1>
      <p>
        SanitiseAI is built as a focused text sanitisation layer. Integrations are rolling out in stages to keep the core
        workflow fast and reliable.
      </p>
      <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">
        <PhRocketLaunch :size="16" weight="fill" aria-hidden="true" />
        <span>Launch sanitiser tool</span>
      </RouterLink>
    </section>

    <section class="integrations__grid">
      <article v-for="card in cards" :key="card.title" class="integrations__card">
        <div class="integrations__card-top">
          <component :is="card.icon" :size="20" weight="duotone" aria-hidden="true" />
          <span>{{ card.status }}</span>
        </div>
        <h2>{{ card.title }}</h2>
        <p>{{ card.description }}</p>
        <RouterLink class="integrations__card-link" to="/tool">
          Use core tool now
          <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
        </RouterLink>
      </article>
    </section>

    <section class="integrations__roadmap">
      <header>
        <PhPlugsConnected :size="18" weight="duotone" aria-hidden="true" />
        <h3>Upcoming platforms</h3>
      </header>

      <ul>
        <li v-for="item in roadmap" :key="item.title">
          <span>{{ item.title }}</span>
          <small>{{ item.tag }}</small>
        </li>
      </ul>
    </section>

    <section class="integrations__final">
      <h2>Need sanitisation today?</h2>
      <p>Use the MVP tool immediately: paste text, sanitise, then copy or export safely.</p>
      <RouterLink class="btn btn--primary" :to="{ path: '/tool', query: { demo: '1' } }">Start sanitising</RouterLink>
    </section>
  </main>
</template>

<style scoped lang="scss">
.integrations {
  width: min(1200px, calc(100% - 2.8rem));
  margin: 0 auto;
  padding-top: 2rem;

  &__eyebrow {
    margin: 0;
    font-size: 0.77rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--accent-1);
    font-weight: 780;
  }

  &__hero {
    max-width: 70ch;

    h1 {
      margin-top: 0.72rem;
      font-size: clamp(2.4rem, 5.5vw, 4.2rem);
      line-height: 0.94;
      letter-spacing: -0.04em;
    }

    p {
      margin: 1rem 0 0;
      color: var(--text-2);
      font-size: 1.03rem;
      line-height: 1.66;
    }

    .btn {
      margin-top: 1.2rem;
      min-height: 48px;
    }
  }

  &__grid {
    margin-top: 2rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
  }

  &__card {
    border-radius: 18px;
    background: var(--surface-0);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 56%);
    box-shadow: var(--shadow-sm);
    padding: 1rem;
    display: grid;
    gap: 0.56rem;

    h2 {
      font-size: 1.08rem;
      line-height: 1.22;
    }

    p {
      margin: 0;
      color: var(--text-2);
      line-height: 1.58;
      font-size: 0.9rem;
    }
  }

  &__card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;

    svg {
      color: var(--accent-1);
    }

    span {
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent-soft), white 46%);
      color: var(--accent-3);
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 760;
      padding: 0.2rem 0.45rem;
    }
  }

  &__card-link {
    width: fit-content;
    margin-top: 0.2rem;
    color: var(--accent-1);
    text-decoration: none;
    font-size: 0.84rem;
    font-weight: 760;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }

  &__roadmap {
    margin-top: 2.2rem;
    border-radius: 18px;
    background: color-mix(in srgb, var(--surface-0), white 12%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 56%);
    box-shadow: var(--shadow-sm);
    padding: 1rem;

    header {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;

      svg {
        color: var(--accent-1);
      }

      h3 {
        margin: 0;
        font-size: 1rem;
      }
    }

    ul {
      margin: 0.8rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.5rem;

      li {
        border-radius: 12px;
        background: var(--surface-0);
        border: 1px solid color-mix(in srgb, var(--border-1), transparent 64%);
        padding: 0.56rem 0.72rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;

        span {
          font-size: 0.9rem;
          font-weight: 640;
          color: var(--text-1);
        }

        small {
          font-size: 0.72rem;
          color: var(--text-3);
          text-transform: uppercase;
          letter-spacing: 0.06em;
          font-weight: 760;
        }
      }
    }
  }

  &__final {
    margin-top: 2.6rem;
    border-radius: 22px;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    color: white;
    padding: 1.4rem;
    text-align: center;

    h2 {
      color: inherit;
      font-size: clamp(1.6rem, 3.6vw, 2.4rem);
      line-height: 1.06;
    }

    p {
      margin: 0.72rem auto 0;
      max-width: 54ch;
      color: color-mix(in srgb, white, transparent 14%);
      font-size: 0.95rem;
      line-height: 1.58;
    }

    .btn {
      margin-top: 1rem;
      min-height: 46px;
      background: white;
      color: var(--accent-3);
      border-color: color-mix(in srgb, white, transparent 24%);
      box-shadow: none;
    }
  }
}

@media (max-width: 980px) {
  .integrations {
    width: min(1200px, calc(100% - 1.2rem));

    &__grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
