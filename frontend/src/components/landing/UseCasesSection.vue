<script setup lang="ts">
type UseCase = {
  title: string
  body: string
  cta: string
}

const useCases = [
  {
    title: 'Developers',
    body: 'Clean logs, stack traces, and support snippets before sharing with assistants.',
    cta: 'Run dev sample',
  },
  {
    title: 'Recruiters',
    body: 'Remove personally identifiable details from CV notes and candidate summaries.',
    cta: 'Run recruiter sample',
  },
  {
    title: 'Consultants',
    body: 'Sanitise client material before drafting recommendations with AI workflows.',
    cta: 'Run consultant sample',
  },
  {
    title: 'Students',
    body: 'Protect private examples and references before sending coursework prompts.',
    cta: 'Run student sample',
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
        <h3>{{ item.title }}</h3>
        <p>{{ item.body }}</p>
        <button class="use-cases__btn" type="button" @click="tryUseCaseExample(item.title)">
          <span class="use-cases__btn-key" aria-hidden="true">↵</span>
          <span>{{ item.cta }}</span>
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
    gap: 0.72rem;
  }

  &__card {
    border: 1px solid var(--border-1);
    border-radius: 16px;
    background:
      linear-gradient(
        160deg,
        color-mix(in srgb, var(--surface-0), white 8%),
        color-mix(in srgb, var(--surface-1), transparent 2%)
      );
    box-shadow: var(--shadow-sm);
    padding: 0.85rem;
    transition: transform 180ms ease, box-shadow 200ms ease, border-color 200ms ease;

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
      transform: translateY(-2px);
      border-color: var(--border-2);
      box-shadow: var(--shadow-md);
    }
  }

  &__btn {
    margin-top: 0.72rem;
    border: 1px solid var(--border-2);
    border-radius: 12px;
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--surface-0), white 14%),
      color-mix(in srgb, var(--surface-1), transparent 2%)
    );
    color: var(--text-1);
    font-size: 0.82rem;
    font-weight: 700;
    padding: 0.38rem 0.72rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
  }

  &__btn:hover {
    border-color: color-mix(in srgb, var(--accent-2), transparent 50%);
    background: color-mix(in srgb, var(--surface-2), var(--accent-2) 11%);
    color: var(--text-1);
    transform: translateY(-1px);
  }

  &__btn:focus-visible {
    outline: 2px solid color-mix(in srgb, var(--accent-2), transparent 32%);
    outline-offset: 2px;
  }

  &__btn-key {
    width: 1.2rem;
    height: 1.2rem;
    border-radius: 6px;
    border: 1px solid var(--border-2);
    background: color-mix(in srgb, var(--surface-0), white 12%);
    display: inline-grid;
    place-items: center;
    font-size: 0.72rem;
    line-height: 1;
    color: var(--accent-2);
    box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--accent-2), transparent 82%);
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
