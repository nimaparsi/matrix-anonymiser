<script setup lang="ts">
import { PhArrowUpRight, PhBriefcase, PhCode, PhGraduationCap, PhUsersThree } from '@phosphor-icons/vue'

type UseCase = {
  title: string
  body: string
  cta: string
  icon: typeof PhCode
}

const useCases = [
  {
    title: 'Developers',
    body: 'Clean logs, stack traces, support tickets, and env snippets before sharing with assistants.',
    cta: 'Try dev example',
    icon: PhCode,
  },
  {
    title: 'Recruiters',
    body: 'Remove personally identifiable details from CV notes and candidate summaries.',
    cta: 'Try recruiter example',
    icon: PhUsersThree,
  },
  {
    title: 'Consultants',
    body: 'Sanitise client material before drafting recommendations with AI workflows.',
    cta: 'Try consultant example',
    icon: PhBriefcase,
  },
  {
    title: 'Students',
    body: 'Protect private examples and references before sending coursework prompts.',
    cta: 'Try student example',
    icon: PhGraduationCap,
  },
] satisfies UseCase[]

function tryUseCaseExample(useCase: string) {
  window.dispatchEvent(
    new CustomEvent('sanitiseai:try-example', {
      detail: { useCase },
    }),
  )

  document.getElementById('demo')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}
</script>

<template>
  <section class="use-cases" aria-labelledby="use-cases-title">
    <header>
      <p class="use-cases__eyebrow">Use cases</p>
      <h2 id="use-cases-title">Who uses SanitiseAI</h2>
    </header>

    <div class="use-cases__grid">
      <article v-for="item in useCases" :key="item.title" class="use-cases__card">
        <div class="use-cases__title-row">
          <component :is="item.icon" class="use-cases__icon" :size="20" weight="duotone" aria-hidden="true" />
          <h3>{{ item.title }}</h3>
        </div>
        <p>{{ item.body }}</p>
        <button class="btn btn--secondary use-cases__btn" type="button" @click="tryUseCaseExample(item.title)">
          <span>{{ item.cta }}</span>
          <PhArrowUpRight :size="14" weight="bold" aria-hidden="true" />
        </button>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.use-cases {
  header h2 {
    margin: 0.5rem 0 0;
    font-size: clamp(1.75rem, 3.8vw, 2.3rem);
    line-height: 1.1;
    letter-spacing: -0.03em;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  &__grid {
    margin-top: 1.18rem;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.9rem;
  }

  &__card {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
    border-radius: 16px;
    background:
      radial-gradient(140% 110% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 74%), transparent 50%),
      var(--surface-0);
    box-shadow: var(--shadow-sm);
    padding: 1rem;
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 200ms ease;

    h3 {
      margin: 0;
      font-size: 1.02rem;
      letter-spacing: -0.01em;
    }

    p {
      margin: 0.5rem 0 0;
      color: var(--text-2);
      font-size: 0.92rem;
      line-height: 1.58;
    }

    &:hover {
      transform: translateY(-4px);
      border-color: color-mix(in srgb, var(--border-strong), transparent 12%);
      box-shadow: var(--shadow-md);
    }
  }

  &__title-row {
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;
  }

  &__icon {
    color: var(--accent-2);
  }

  &__btn {
    margin-top: 0.76rem;
    min-height: 41px;
    width: fit-content;
    padding-inline: 0.8rem;
  }
}

@media (max-width: 980px) {
  .use-cases {
    &__grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
