import { createRouter, createWebHistory, createMemoryHistory } from 'vue-router'
const HomePage = () => import('../pages/HomePage.vue')
const ToolPage = () => import('../pages/ToolPage.vue')
const IntegrationsPage = () => import('../pages/IntegrationsPage.vue')
const PrivacyPage = () => import('../pages/PrivacyPage.vue')
const SecurityPage = () => import('../pages/SecurityPage.vue')
const TermsPage = () => import('../pages/TermsPage.vue')
const ContactPage = () => import('../pages/ContactPage.vue')
const UseCasePage = () => import('../pages/UseCasePage.vue')

const SITE_URL = 'https://sanitiseai.com'

type RouteMetaConfig = {
  title: string
  description: string
  canonical: string
}

const defaultMeta: RouteMetaConfig = {
  title: 'SanitiseAI | Text Anonymiser for AI Prompts, Documents and PII',
  description:
    'SanitiseAI anonymises sensitive text before it is shared with AI tools, documents, support workflows, and code review. Detect PII, secrets, IDs, emails, and addresses.',
  canonical: `${SITE_URL}/`,
}

function applyRouteMeta(meta: RouteMetaConfig) {
  if (typeof document === 'undefined') return
  document.title = meta.title

  const updateMeta = (selector: string, content: string) => {
    const node = document.querySelector<HTMLMetaElement>(selector)
    if (node) node.setAttribute('content', content)
  }

  let canonical = document.querySelector<HTMLLinkElement>('#canonical-link')
  if (!meta.canonical) canonical?.remove()
  else {
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.id = 'canonical-link'
      canonical.rel = 'canonical'
      document.head.appendChild(canonical)
    }
    canonical.href = meta.canonical
  }

  updateMeta('#meta-description', meta.description)
  updateMeta('#meta-og-title', meta.title)
  updateMeta('#meta-og-description', meta.description)
  updateMeta('#meta-og-url', meta.canonical)
  updateMeta('#meta-twitter-title', meta.title)
  updateMeta('#meta-twitter-description', meta.description)
}

export function makeRouter() {
const router = createRouter({
  history: typeof window === 'undefined' ? createMemoryHistory() : createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: {
        title: 'SanitiseAI | AI Text Anonymiser and PII Redaction Tool',
        description:
          'Anonymise sensitive documents, AI prompts, support notes, medical records, legal drafts, contracts, and developer logs before sharing them with AI tools.',
        canonical: `${SITE_URL}/`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/tool',
      name: 'tool',
      component: ToolPage,
      meta: {
        title: 'Free Text Anonymiser Tool | PII Redaction for AI Prompts',
        description:
          'Paste text into SanitiseAI to detect names, emails, phone numbers, addresses, dates, IDs, usernames, IPs, passwords, API keys, and secrets, then copy anonymised output.',
        canonical: `${SITE_URL}/tool`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/integrations',
      name: 'integrations',
      component: IntegrationsPage,
      meta: {
        title: 'Integrations | SanitiseAI Workflow Compatibility',
        description:
          'See how SanitiseAI fits into browser, API, and future workflow integrations. Review what is available now and what is planned next.',
        canonical: `${SITE_URL}/integrations`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: PrivacyPage,
      meta: {
        title: 'Privacy | How SanitiseAI Handles Sensitive Text',
        description:
          'Understand how SanitiseAI approaches request-scoped processing, privacy controls, and handling of sensitive text before downstream sharing.',
        canonical: `${SITE_URL}/privacy`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/security',
      name: 'security',
      component: SecurityPage,
      meta: {
        title: 'Security | Controls for Sensitive Text Processing',
        description:
          'Review SanitiseAI security controls, encrypted transport, controlled updates, and operational safeguards for sanitising sensitive text.',
        canonical: `${SITE_URL}/security`,
      } satisfies RouteMetaConfig,
    },

    {
      path: '/use-cases/:slug',
      name: 'use-case',
      component: UseCasePage,
      meta: {
        title: 'Text Anonymisation Use Cases | SanitiseAI',
        description:
          'See how SanitiseAI helps anonymise AI prompts, legal documents, medical notes, support handoffs, developer logs, and sensitive documents before sharing.',
        canonical: `${SITE_URL}/use-cases/anonymise-text-before-chatgpt`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/terms',
      name: 'terms',
      component: TermsPage,
      meta: {
        title: 'Terms | SanitiseAI',
        description:
          'Read the current terms governing use of SanitiseAI and its text sanitisation workflow.',
        canonical: `${SITE_URL}/terms`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactPage,
      meta: {
        title: 'Contact | Speak With SanitiseAI',
        description:
          'Contact SanitiseAI for product questions, rollout support, and security-related enquiries about sensitive text workflows.',
        canonical: `${SITE_URL}/contact`,
      } satisfies RouteMetaConfig,
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../pages/NotFoundPage.vue') },
  ],
  // Retire old example links without triggering a sanitisation request.
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) {
      return {
        el: to.hash,
        top: 90,
        behavior: 'smooth',
      }
    }
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.name === 'use-case' && !useCaseMeta[String(to.params.slug)]) return { name: 'not-found', params: { pathMatch: to.path.slice(1).split('/') }, replace: true }
  if ('demo' in to.query) {
    const { demo: _demo, ...query } = to.query
    return { path: to.path, query, hash: to.hash, replace: true }
  }
})

router.afterEach((to) => {
  if (typeof document !== 'undefined') {
    document.querySelector('meta[name=robots]')?.setAttribute('content', to.name === 'not-found' ? 'noindex, follow' : 'index, follow')
    document.querySelectorAll('script[data-page-schema]').forEach(node => node.remove())
    if (to.name === 'home') {
      const node = document.createElement('script')
      node.type = 'application/ld+json'
      node.dataset.pageSchema = ''
      node.textContent = JSON.stringify({ '@context': 'https://schema.org', '@type': 'WebSite', name: 'SanitiseAI', alternateName: 'Sanitise AI', url: SITE_URL + '/' })
      document.head.appendChild(node)
    }
  }
  applyRouteMeta(resolveMeta(to))
})
return router
}

const useCaseMeta: Record<string, RouteMetaConfig> = {
  'anonymise-text-before-chatgpt': {
    title: 'Anonymise Text Before ChatGPT | SanitiseAI',
    description: 'Use SanitiseAI to anonymise sensitive text before pasting it into ChatGPT, Claude, Gemini, or another AI assistant.',
    canonical: `${SITE_URL}/use-cases/anonymise-text-before-chatgpt`,
  },
  'pii-redaction-tool': {
    title: 'PII Redaction Tool for Sensitive Text | SanitiseAI',
    description: 'Detect and redact PII including names, emails, phones, addresses, dates, IDs, usernames, and other sensitive details.',
    canonical: `${SITE_URL}/use-cases/pii-redaction-tool`,
  },
  'anonymise-legal-documents': {
    title: 'Anonymise Legal Documents Before AI Review | SanitiseAI',
    description: 'Clean legal drafts, contract excerpts, redlines, renewal clauses, matter notes, and invoice references before external or AI review.',
    canonical: `${SITE_URL}/use-cases/anonymise-legal-documents`,
  },
  'remove-secrets-from-logs': {
    title: 'Remove Secrets From Logs Before Sharing | SanitiseAI',
    description: 'Sanitise developer logs, stack traces, API keys, passwords, tokens, SSH keys, IP addresses, and usernames before AI debugging.',
    canonical: `${SITE_URL}/use-cases/remove-secrets-from-logs`,
  },
  'medical-note-anonymiser': {
    title: 'Medical Note Anonymiser for AI Summaries | SanitiseAI',
    description: 'Anonymise referral notes, appointment summaries, patient contacts, dates of birth, health IDs, and addresses before AI summarisation.',
    canonical: `${SITE_URL}/use-cases/medical-note-anonymiser`,
  },
  'document-redaction-before-ai': {
    title: 'Document Redaction Before AI Review | SanitiseAI',
    description: 'Paste or upload text from documents and redact sensitive details before summarising, rewriting, or analysing with AI tools.',
    canonical: `${SITE_URL}/use-cases/document-redaction-before-ai`,
  },
}

export function resolveMeta(to: any): RouteMetaConfig {
  if (to.name === 'not-found') return { title: 'Page not found | SanitiseAI', description: 'This page does not exist. Open the sanitiser or return to the homepage.', canonical: '' }
  const meta = (to.meta as Partial<RouteMetaConfig>) || {}
  const routeMeta = to.name === 'use-case' ? useCaseMeta[String(to.params.slug)] : undefined
  return {
    title: routeMeta?.title || meta.title || defaultMeta.title,
    description: routeMeta?.description || meta.description || defaultMeta.description,
    canonical: routeMeta?.canonical || meta.canonical || defaultMeta.canonical,
  }
}

export default makeRouter()
