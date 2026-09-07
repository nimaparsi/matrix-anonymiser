import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
import App from './App.vue'
import { makeRouter, resolveMeta } from './router'
export async function render(url: string) {
  const router = makeRouter()
  const app = createSSRApp(App).use(router)
  await router.push(url)
  await router.isReady()
  const context: { modules?: Set<string> } = {}
  const html = await renderToString(app, context)
  return { html, modules: [...(context.modules || [])], meta: resolveMeta(router.currentRoute.value), missing: router.currentRoute.value.name === 'not-found' }
}
