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
    <nav class="usecase-page__breadcrumbs" aria-label="Breadcrumb">
      <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem"><RouterLink itemprop="item" to="/"><span itemprop="name">Home</span></RouterLink><meta itemprop="position" content="1" /></li>
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem"><RouterLink itemprop="item" to="/#use-cases"><span itemprop="name">Use cases</span></RouterLink><meta itemprop="position" content="2" /></li>
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem"><span itemprop="name" aria-current="page">{{ page.eyebrow }}</span><meta itemprop="position" content="3" /></li>
      </ol>
    </nav>
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
      <p class="usecase-page__eyebrow">In practice</p>
      <h2>A worked example</h2>
      <p>Synthetic input and expected readable output. This small example demonstrates one replacement, not complete coverage. Try it in the tool and review the result.</p>
      <div class="usecase-page__comparison"><article><h3>01 / Source text</h3><pre>{{ example.input }}</pre></article><article><h3>02 / Expected output</h3><pre>{{ example.output }}</pre></article></div>
      <h3>Follow the workflow</h3>
      <ol><li v-for="step in example.steps" :key="step">{{ step }}</li></ol>
      <aside class="usecase-page__review"><PhShieldCheck :size="24" aria-hidden="true" /><div><h3>Where human review matters</h3><p>{{ example.limit }}</p><RouterLink to="/security#evaluation">Evaluation method and known limitations <span aria-hidden="true">→</span></RouterLink></div></aside>
    </section>
    <section class="usecase-page__related" aria-labelledby="related-title">
      <p class="usecase-page__eyebrow">Explore further</p><h2 id="related-title">Related use cases</h2>
      <p>Find a workflow that fits the text you need to share.</p>
      <div class="usecase-page__related-grid">
        <RouterLink v-for="item in Object.values(useCases).filter(item => item.slug !== page.slug)" :key="item.slug" :to="'/use-cases/' + item.slug" class="usecase-page__related-card">
          <span class="usecase-page__related-icon"><component :is="item.icon" :size="24" weight="duotone" aria-hidden="true" /></span>
          <h3>{{ item.eyebrow }}</h3><p>{{ item.audience }}</p>
          <span class="usecase-page__related-action">Explore use case <PhArrowRight :size="18" aria-hidden="true" /></span>
        </RouterLink>
      </div>
    </section>
    <section class="usecase-page__cta"><div><h2>Put the workflow into practice.</h2><p>Start with an example. Review every result before sharing.</p></div><RouterLink class="btn btn--primary" to="/tool">Open sanitiser <PhArrowRight :size="18" aria-hidden="true" /></RouterLink></section>
  </main>
</template>

<style scoped lang="scss">
.usecase-page {
  --section-space: clamp(3rem, 6vw, 5rem);
  width: min(1180px, calc(100% - 3rem)); margin: 0 auto; padding: 1.5rem 0 1rem;
  h1, h2, h3 { color: var(--text-1); }
  h2 { font-size: clamp(1.75rem, 3vw, 2.5rem); line-height: 1.18; letter-spacing: -.035em; margin: 0 0 1rem; }
  h3 { font-size: 1.125rem; line-height: 1.4; margin: 0 0 .75rem; }
  p { color: var(--text-2); font-size: 1rem; line-height: 1.75; margin: 0 0 1.25rem; max-width: 72ch; }
  a:focus-visible { outline: 3px solid var(--accent-1); outline-offset: 5px; }
  &__breadcrumbs { margin-bottom: 2.5rem; ol { display: flex; flex-wrap: wrap; gap: .5rem .75rem; list-style: none; margin: 0; padding: 0; } li { font-size: .8125rem; line-height: 1.6; color: var(--text-2); } li + li::before { content: '/'; margin-right: .75rem; color: var(--text-3); } a { color: var(--text-2); text-underline-offset: 4px; } }
  &__hero { display: grid; grid-template-columns: minmax(0,1.5fr) minmax(260px,1fr); gap: clamp(2rem,5vw,4rem); align-items: center; }
  h1 { font-size: clamp(2.5rem,4.5vw,3.5rem); line-height: 1.12; letter-spacing: -.04em; margin: 1.25rem 0 1.5rem; max-width: 19ch; span { color: var(--accent-1); } }
  &__eyebrow { font-family: 'Space Grotesk',sans-serif; font-size: .6875rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: .14em; color: var(--accent-1) !important; margin-bottom: .75rem !important; }
  &__actions { display: flex; flex-wrap: wrap; gap: .75rem; margin-top: 1.75rem; }
  &__panel { background: var(--surface-0); border-radius: var(--radius-xl); padding: clamp(1.5rem,3vw,2rem); display: grid; gap: 1.5rem; svg { color: var(--accent-1); } strong { font-size: 1.25rem; line-height: 1.5; font-weight: 600; } ul { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: .5rem; } li { background: var(--surface-2); padding: .4rem .65rem; border-radius: 999px; font-size: .75rem; color: var(--text-2); } }
  &__grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 1.5rem; margin: var(--section-space) 0; article { background: var(--surface-0); padding: 2rem; border-radius: var(--radius-xl); } h2 { font-size: 1.375rem; } ul { display: grid; gap: 1rem; list-style: none; padding: 0; margin: 1.5rem 0 0; } li { display: flex; align-items: start; gap: .75rem; color: var(--text-2); line-height: 1.5; } svg { flex-shrink: 0; color: var(--accent-1); margin-top: .25rem; } }
  &__answer { > h3 { margin-top: 2.5rem; } ol { list-style: none; counter-reset: steps; display: grid; gap: 1rem; padding: 0; margin: 1.5rem 0 2.5rem; } ol li { counter-increment: steps; display: flex; align-items: start; gap: 1rem; line-height: 1.75; color: var(--text-2); } ol li::before { content: counter(steps); display: grid; place-items: center; flex: 0 0 2rem; height: 2rem; background: var(--accent-soft); color: var(--accent-3); border-radius: 50%; font-weight: 700; font-size: .8125rem; } }
  &__comparison { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 1.5rem; margin: 2rem 0; article { padding: 1.75rem; background: var(--surface-0); border-radius: var(--radius-xl); } article:last-child { background: color-mix(in srgb,var(--accent-soft),white 65%); } h3 { font-family: 'Space Grotesk',sans-serif; font-size: .75rem; letter-spacing: .06em; text-transform: uppercase; color: var(--text-2); margin-bottom: 1.25rem; } pre { white-space: pre-wrap; overflow-wrap: anywhere; font-family: 'Space Grotesk',sans-serif; font-size: .9375rem; line-height: 1.8; margin: 0; color: var(--text-1); } }
  &__review { display: flex; gap: 1rem; background: var(--surface-2); border-radius: var(--radius-xl); padding: 1.75rem; svg { flex-shrink: 0; color: var(--accent-1); } p { font-size: .9375rem; } a { font-size: .875rem; color: var(--accent-3); text-underline-offset: 4px; } }
  &__related { margin-top: var(--section-space); }
  &__related-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1.25rem; margin-top: 2rem; }
  &__related-card { display: flex; flex-direction: column; padding: 1.75rem; background: var(--surface-0); border-radius: var(--radius-xl); text-decoration: none; transition: background .2s ease; h3 { margin: 1.25rem 0 .75rem; font-size: 1.125rem; } p { font-size: .875rem; margin-bottom: 1.5rem; } &:hover { background: color-mix(in srgb,var(--accent-soft),white 65%); } }
  &__related-icon { display: grid; place-items: center; width: 2.75rem; height: 2.75rem; border-radius: var(--radius-md); background: var(--accent-soft); color: var(--accent-1); }
  &__related-action { display: flex; align-items: center; justify-content: space-between; gap: .75rem; margin-top: auto; color: var(--accent-1); font-size: .8125rem; font-weight: 700; }
  &__cta { display: flex; align-items: center; justify-content: space-between; gap: 2rem; margin-top: var(--section-space); padding: clamp(1.5rem,4vw,3rem); background: var(--surface-2); border-radius: var(--radius-xl); h2 { font-size: clamp(1.5rem,3vw,2rem); } p { margin: 0; } .btn { flex-shrink: 0; } }
}
@media(max-width: 900px) { .usecase-page { &__related-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } &__hero { gap: 1.5rem; } } }
@media(max-width: 640px) { .usecase-page { width: calc(100% - 2rem); &__hero, &__grid, &__comparison, &__related-grid { grid-template-columns: 1fr; } &__grid article, &__comparison article, &__related-card { padding: 1.5rem; } &__cta { flex-direction: column; align-items: start; } &__breadcrumbs { margin-bottom: 2rem; } } }
@media(prefers-reduced-motion: reduce) { .usecase-page__related-card { transition: none; } }
</style>
