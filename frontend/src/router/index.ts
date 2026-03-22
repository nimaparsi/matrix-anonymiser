import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import ToolPage from '../pages/ToolPage.vue'
import IntegrationsPage from '../pages/IntegrationsPage.vue'
import PrivacyPage from '../pages/PrivacyPage.vue'
import SecurityPage from '../pages/SecurityPage.vue'
import TermsPage from '../pages/TermsPage.vue'
import ContactPage from '../pages/ContactPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/tool',
      name: 'tool',
      component: ToolPage,
    },
    {
      path: '/integrations',
      name: 'integrations',
      component: IntegrationsPage,
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: PrivacyPage,
    },
    {
      path: '/security',
      name: 'security',
      component: SecurityPage,
    },
    {
      path: '/terms',
      name: 'terms',
      component: TermsPage,
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactPage,
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

export default router
