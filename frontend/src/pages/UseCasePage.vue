<script setup lang="ts">
import { computed } from 'vue'
import workflowExamples from '../lib/workflowExamples.json'
import { RouterLink, useRoute } from 'vue-router'
import { PhArrowRight, PhCheckCircle, PhCode, PhFileText, PhFirstAidKit, PhGavel, PhRobot, PhShieldCheck } from '@phosphor-icons/vue'

type UseCase = {
  slug: string
  eyebrow: string
  title: string
  accent: string
  intro: string
  audience: string
  examples: string[]
  removes: string[]
  keeps: string[]
  icon: typeof PhRobot
}

const useCases: Record<string, UseCase> = {
  'anonymise-text-before-chatgpt': {
    slug: 'anonymise-text-before-chatgpt',
    eyebrow: 'AI prompt privacy',
    title: 'Anonymise text before using',
    accent: 'ChatGPT or AI tools.',
    intro:
      'SanitiseAI helps turn sensitive notes, emails, transcripts, and document excerpts into safer AI prompts by replacing personal and operational identifiers with readable placeholders.',
    audience: 'For people who want useful AI output without pasting raw private data into an assistant.',
    examples: ['Client summaries', 'Support escalations', 'Meeting notes', 'Medical or HR notes', 'Contract excerpts'],
    removes: ['Names and personal contacts', 'Addresses and dates of birth', 'Customer IDs and invoice references', 'Usernames and account identifiers'],
    keeps: ['Core facts', 'Structure and chronology', 'Task-relevant context', 'Readable placeholder labels'],
    icon: PhRobot,
  },
  'pii-redaction-tool': {
    slug: 'pii-redaction-tool',
    eyebrow: 'PII redaction tool',
    title: 'Detect and redact PII from',
    accent: 'sensitive text.',
    intro:
      'Use SanitiseAI to detect common personally identifiable information and replace it with consistent tokens before content is shared, reviewed, or copied into downstream tools.',
    audience: 'For teams handling customer, employee, patient, candidate, or supplier text.',
    examples: ['Names', 'Emails', 'Phone numbers', 'Addresses', 'Dates and IDs'],
    removes: ['Direct identifiers', 'Contact routes', 'Operational IDs', 'Location details'],
    keeps: ['Document format', 'Sentence meaning', 'Entity counts', 'Reviewable output'],
    icon: PhShieldCheck,
  },
  'anonymise-legal-documents': {
    slug: 'anonymise-legal-documents',
    eyebrow: 'Legal document anonymisation',
    title: 'Anonymise legal drafts and',
    accent: 'contract excerpts.',
    intro:
      'Prepare legal notes, first-page contract excerpts, renewal clauses, redlines, and matter summaries for external review while reducing exposure of names, contacts, addresses, and references.',
    audience: 'For lawyers, founders, operators, and consultants preparing legal text for AI or external review.',
    examples: ['MSA amendments', 'Renewal clauses', 'Redline notes', 'Matter updates', 'Invoice references'],
    removes: ['Personal names', 'Law firm and client contacts', 'Addresses', 'Sensitive references'],
    keeps: ['Commercial terms', 'Clause context', 'Risk language', 'Timeline details where useful'],
    icon: PhGavel,
  },
  'remove-secrets-from-logs': {
    slug: 'remove-secrets-from-logs',
    eyebrow: 'Developer log sanitisation',
    title: 'Remove secrets from logs before',
    accent: 'sharing them with AI.',
    intro:
      'SanitiseAI helps developers clean stack traces, deployment logs, support payloads, and environment snippets before sending them to AI tools, vendors, or public issue trackers.',
    audience: 'For developers, support engineers, DevOps teams, and security-conscious product teams.',
    examples: ['API keys', 'Passwords', 'JWTs', 'SSH keys', 'IP addresses and usernames'],
    removes: ['Credentials', 'Access tokens', 'Network identifiers', 'Personal support contacts'],
    keeps: ['Error messages', 'Sequence of events', 'Service names where safe', 'Debugging context'],
    icon: PhCode,
  },
  'medical-note-anonymiser': {
    slug: 'medical-note-anonymiser',
    eyebrow: 'Medical note anonymiser',
    title: 'Anonymise medical notes before',
    accent: 'AI summarisation.',
    intro:
      'Use SanitiseAI to prepare referral notes, appointment summaries, and clinical admin text by replacing patient names, dates of birth, NHS-style numbers, contact details, and addresses.',
    audience: 'For health-adjacent admin and research workflows that need safer text before analysis or drafting.',
    examples: ['Referral notes', 'Discharge summaries', 'Appointment messages', 'Patient callbacks', 'Clinic admin notes'],
    removes: ['Patient names', 'DOB and health IDs', 'Clinician contact details', 'Home addresses'],
    keeps: ['Clinical topic', 'Symptoms and next steps', 'Non-identifying chronology', 'Structured placeholders'],
    icon: PhFirstAidKit,
  },
  'document-redaction-before-ai': {
    slug: 'document-redaction-before-ai',
    eyebrow: 'Document redaction before AI',
    title: 'Clean documents before',
    accent: 'AI review.',
    intro:
      'Paste or upload text from documents and turn sensitive passages into structured anonymised output before summarising, rewriting, or analysing with AI tools.',
    audience: 'For anyone handling PDFs, notes, contracts, transcripts, policies, reports, or operational documents.',
    examples: ['PDF text excerpts', 'Meeting notes', 'Reports', 'Policy drafts', 'Customer documents'],
    removes: ['People and contacts', 'Addresses and IDs', 'Invoices and references', 'Secrets and system values'],
    keeps: ['Document order', 'Headings', 'Task-relevant facts', 'Copyable plain text'],
    icon: PhFileText,
  },
}

const route = useRoute()
const page = computed(() => useCases[String(route.params.slug)])
const example = computed(() => workflowExamples[page.value.slug as keyof typeof workflowExamples])
</script>

<template>
  <main class="usecase-page">
    <section class="usecase-page__hero">
      <div>
        <p class="usecase-page__eyebrow">{{ page.eyebrow }}</p>
        <h1>{{ page.title }} <span>{{ page.accent }}</span></h1>
        <p>{{ page.intro }}</p>
        <div class="usecase-page__actions">
          <RouterLink class="btn btn--primary" to="/tool">
            Try SanitiseAI
            <PhArrowRight :size="14" weight="bold" aria-hidden="true" />
          </RouterLink>
          <RouterLink class="btn btn--secondary" to="/privacy">Review privacy</RouterLink>
        </div>
      </div>
      <aside class="usecase-page__panel" aria-label="Use case summary">
        <component :is="page.icon" :size="34" weight="duotone" aria-hidden="true" />
        <strong>{{ page.audience }}</strong>
        <ul>
          <li v-for="item in page.examples" :key="item">{{ item }}</li>
        </ul>
      </aside>
    </section>

    <section class="usecase-page__grid" aria-label="Sanitisation behaviour">
      <article>
        <h2>What to check for</h2>
        <ul>
          <li v-for="item in page.removes" :key="item"><PhCheckCircle :size="16" weight="fill" aria-hidden="true" />{{ item }}</li>
        </ul>
      </article>
      <article>
        <h2>What to preserve during review</h2>
        <ul>
          <li v-for="item in page.keeps" :key="item"><PhCheckCircle :size="16" weight="fill" aria-hidden="true" />{{ item }}</li>
        </ul>
      </article>
    </section>

    <section class="usecase-page__answer">
      <h2>A worked example</h2>
      <p>Synthetic input and expected readable output. This small example demonstrates one replacement, not complete coverage. Try it in the tool and review the result.</p>
      <div class="usecase-page__grid"><article><h3>Before</h3><pre>{{ example.input }}</pre></article><article><h3>Expected output</h3><pre>{{ example.output }}</pre></article></div>
      <h3>Follow the workflow</h3>
      <ol><li v-for="step in example.steps" :key="step">{{ step }}</li></ol>
      <h3>Where human review matters</h3><p>{{ example.limit }}</p>
      <RouterLink to="/security#evaluation">Read our evaluation method and known limitations</RouterLink>
    </section>
    <section class="usecase-page__answer">
      <h2>Related workflows</h2>
      <ul><li v-for="item in Object.values(useCases).filter(item => item.slug !== page.slug)" :key="item.slug"><RouterLink :to="'/use-cases/' + item.slug">{{ item.eyebrow }}</RouterLink></li></ul>
    </section>
    <section class="usecase-page__answer">
      <p class="usecase-page__eyebrow">Direct answer</p>
      <h2>Use SanitiseAI when you need a focused text anonymiser before sharing content with AI.</h2>
      <p>
        The workflow is simple: paste or upload text, run detection, review readable placeholder tokens, then copy or export the sanitised result. It is built for text preparation, not document storage or team workspaces.
      </p>
    </section>
  </main>
</template>

<style scoped lang="scss">
.usecase-page {
  pre { white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.7; font-size: .95rem; }
  ol li { margin: .8rem 0; line-height: 1.7; }
  width: min(1180px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 2.2rem;

  &__hero {
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.65fr);
    gap: 1.1rem;
    align-items: stretch;
  }

  &__eyebrow {
    margin: 0;
    width: fit-content;
    border-radius: 999px;
    padding: 0.42rem 0.78rem;
    background: color-mix(in srgb, var(--accent-soft), white 38%);
    color: var(--accent-1);
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 780;
  }

  h1 {
    margin: 1rem 0 0;
    max-width: 12ch;
    font-size: clamp(3rem, 7vw, 5.8rem);
    line-height: 0.95;
    letter-spacing: -0.055em;

    span {
      color: var(--accent-1);
    }
  }

  &__hero > div > p:not(.usecase-page__eyebrow) {
    margin: 1.1rem 0 0;
    max-width: 58ch;
    color: var(--text-2);
    font-size: 1.08rem;
    line-height: 1.66;
  }

  &__actions {
    margin-top: 1.3rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
  }

  &__panel,
  &__grid article,
  &__answer {
    border-radius: var(--radius-xl);
    background:
      radial-gradient(120% 100% at 100% 0%, color-mix(in srgb, var(--accent-soft), white 72%), transparent 46%),
      var(--surface-0);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 46%);
    box-shadow: var(--shadow-sm);
  }

  &__panel {
    padding: 1.35rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 1rem;

    svg {
      color: var(--accent-1);
    }

    strong {
      display: block;
      color: var(--text-1);
      font-size: 1.36rem;
      line-height: 1.16;
      letter-spacing: -0.03em;
    }

    ul {
      list-style: none;
      margin: auto 0 0;
      padding: 0;
      display: flex;
      flex-wrap: wrap;
      gap: 0.42rem;
    }

    li {
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-2), white 20%);
      color: var(--text-2);
      font-size: 0.78rem;
      font-weight: 700;
      padding: 0.36rem 0.62rem;
    }
  }

  &__grid {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;

    article {
      padding: 1.35rem;
    }

    h2 {
      margin: 0;
      font-size: clamp(1.6rem, 3vw, 2.2rem);
      line-height: 1.08;
      letter-spacing: -0.04em;
    }

    ul {
      list-style: none;
      padding: 0;
      margin: 1rem 0 0;
      display: grid;
      gap: 0.65rem;
    }

    li {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--text-2);
      font-weight: 650;
    }

    svg {
      color: var(--accent-1);
      flex-shrink: 0;
    }
  }

  &__answer {
    margin-top: 1rem;
    padding: clamp(1.4rem, 4vw, 2.4rem);

    h2 {
      margin: 0.75rem 0 0;
      max-width: 760px;
      font-size: clamp(2rem, 4.8vw, 3.6rem);
      line-height: 1;
      letter-spacing: -0.05em;
    }

    p:not(.usecase-page__eyebrow) {
      margin: 1rem 0 0;
      max-width: 76ch;
      color: var(--text-2);
      font-size: 1rem;
      line-height: 1.65;
    }
  }
}

@media (max-width: 860px) {
  .usecase-page {
    width: min(1180px, calc(100% - 1rem));

    &__hero,
    &__grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
