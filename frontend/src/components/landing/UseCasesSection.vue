<script setup lang="ts">
type UseCase = {
  title: string
  body: string
}

const useCases = [
  {
    title: 'Developers',
    body: 'Clean logs, stack traces, and support snippets before sharing with assistants.',
  },
  {
    title: 'Recruiters',
    body: 'Remove personally identifiable details from CV notes and candidate summaries.',
  },
  {
    title: 'Consultants',
    body: 'Sanitise client material before drafting recommendations with AI workflows.',
  },
  {
    title: 'Students',
    body: 'Protect private examples and references before sending coursework prompts.',
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
        <button class="use-cases__btn" type="button" @click="tryUseCaseExample(item.title)">Try example</button>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.use-cases {
  header h2 {
    margin: 0.45rem 0 0;
    color: #0f172a;
    font-size: clamp(1.45rem, 3.4vw, 1.95rem);
    letter-spacing: -0.02em;
  }

  &__eyebrow {
    margin: 0;
    color: #1d4ed8;
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
    border: 1px solid #dbe4f5;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
    padding: 0.85rem;

    h3 {
      margin: 0;
      color: #0f172a;
      font-size: 1rem;
    }

    p {
      margin: 0.46rem 0 0;
      color: #475569;
      font-size: 0.88rem;
      line-height: 1.52;
    }
  }

  &__btn {
    margin-top: 0.72rem;
    border: 1px solid #c6d7f1;
    border-radius: 999px;
    background: #f8fbff;
    color: #1d4ed8;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 0.36rem 0.76rem;
    cursor: pointer;
    transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
  }

  &__btn:hover {
    border-color: #93c5fd;
    background: #eff6ff;
    color: #1e40af;
    transform: translateY(-1px);
  }

  &__btn:focus-visible {
    outline: 2px solid #2563eb;
    outline-offset: 2px;
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
