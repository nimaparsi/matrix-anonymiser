import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import ToolPage from '../pages/ToolPage.vue'
import IntegrationsPage from '../pages/IntegrationsPage.vue'
import PrivacyPage from '../pages/PrivacyPage.vue'
import SecurityPage from '../pages/SecurityPage.vue'
import TermsPage from '../pages/TermsPage.vue'
import ContactPage from '../pages/ContactPage.vue'

const SITE_URL = 'https://sanitiseai.com'

type RouteMetaConfig = {
  title: string
  description: string
  canonical: string
}

const defaultMeta: RouteMetaConfig = {
  title: 'SanitiseAI - AI Text Anonymiser for PII Redaction',
  description:
    'SanitiseAI is an AI text anonymiser for PII redaction. Detect names, emails, phone numbers, IDs, secrets, and other sensitive details before sharing text with AI tools.',
  canonical: `${SITE_URL}/`,
}

function applyRouteMeta(meta: RouteMetaConfig) {
  document.title = meta.title

  const updateMeta = (selector: string, content: string) => {
    const node = document.querySelector<HTMLMetaElement>(selector)
    if (node) node.setAttribute('content', content)
  }

  const canonical = document.querySelector<HTMLLinkElement>('#canonical-link')
  if (canonical) canonical.setAttribute('href', meta.canonical)

  updateMeta('#meta-description', meta.description)
  updateMeta('#meta-og-title', meta.title)
  updateMeta('#meta-og-description', meta.description)
  updateMeta('#meta-og-url', meta.canonical)
  updateMeta('#meta-twitter-title', meta.title)
  updateMeta('#meta-twitter-description', meta.description)
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: {
        title: 'SanitiseAI - AI Text Anonymiser for Sensitive Documents',
        description:
          'Use SanitiseAI to anonymise sensitive documents, prompts, notes, logs, and contracts before sharing them with AI tools or external workflows.',
        canonical: `${SITE_URL}/`,
      } satisfies RouteMetaConfig,
    },
    {
      path: '/tool',
      name: 'tool',
      component: ToolPage,
      meta: {
        title: 'SanitiseAI Tool - Paste, Detect, and Anonymise Text',
        description:
          'Use the SanitiseAI tool to detect emails, phone numbers, addresses, IDs, secrets, and other sensitive text, then export structured anonymised output.',
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
  ],
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

router.afterEach((to) => {
  const meta = (to.meta as Partial<RouteMetaConfig>) || {}
  applyRouteMeta({
    title: meta.title || defaultMeta.title,
    description: meta.description || defaultMeta.description,
    canonical: meta.canonical || defaultMeta.canonical,
  })
})

export default router
