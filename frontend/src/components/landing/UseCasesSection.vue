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
    body: 'Clean logs, stack traces, and support snippets before sharing with assistants.',
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
          <PhArrowUpRight :size="15" weight="bold" aria-hidden="true" />
        </button>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.use-cases {
  header h2 {
    margin: 0.45rem 0 0;
    color: var(--text-1);
    font-size: clamp(1.45rem, 3.4vw, 1.95rem);
    letter-spacing: -0.02em;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  &__grid {
    margin-top: 0.95rem;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.8rem;
  }

  &__card {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: 18px;
    background:
      radial-gradient(130% 120% at 100% 0%, color-mix(in srgb, var(--accent-2), transparent 90%), transparent 48%),
      linear-gradient(
        160deg,
        color-mix(in srgb, var(--surface-0), white 4%),
        color-mix(in srgb, var(--surface-1), transparent 2%)
      );
    box-shadow: var(--shadow-sm);
    padding: 0.94rem;
    transition: transform 180ms ease, box-shadow 200ms ease, border-color 200ms ease;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 12px;
      right: 12px;
      height: 1px;
      background: linear-gradient(
        90deg,
        transparent,
        color-mix(in srgb, var(--accent-2), transparent 60%),
        color-mix(in srgb, var(--accent-3), transparent 60%),
        transparent
      );
      pointer-events: none;
    }

    h3 {
      margin: 0;
      color: var(--text-1);
      font-size: 1rem;
    }

    p {
      margin: 0.46rem 0 0;
      color: var(--text-2);
      font-size: 0.88rem;
      line-height: 1.52;
    }

    &:hover {
      transform: translateY(-4px);
      border-color: var(--border-2);
      box-shadow: var(--shadow-md);
    }
  }

  &__title-row {
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;
  }

  &__icon {
    color: color-mix(in srgb, var(--accent-2), var(--accent-1) 40%);
  }

  &__btn {
    margin-top: 0.72rem;
    min-height: 41px;
    padding-inline: 0.72rem;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 980px) {
  .use-cases {
    &__grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
}

@media (max-width: 640px) {
  .use-cases {
    &__grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
