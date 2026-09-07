import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { render } from '../.ssr/entry-server.js'
const manifest = JSON.parse(await readFile('dist/.vite/manifest.json', 'utf8'))
const template = await readFile('dist/index.html', 'utf8')
const sitemap = await readFile('public/sitemap.xml', 'utf8')
const routes = [...sitemap.matchAll(/<loc>https:\/\/sanitiseai\.com([^<]*)<\/loc>/g)].map(m => m[1] || '/')
const escape = s => s.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
for (const route of [...routes, '/404']) {
  const { html, meta, missing, modules } = await render(route)
  if (missing && route !== '/404') throw new Error(`Sitemap route does not exist: ${route}`)
  const styles = new Set()
  const visited = new Set()
  function collect(key) {
    if (visited.has(key)) return
    visited.add(key)
    const chunk = manifest[key]
    if (!chunk) return
    for (const css of chunk.css || []) styles.add(css)
    for (const dependency of chunk.imports || []) collect(dependency)
  }
  modules.forEach(collect)
  let page = template.replace('</head>', [...styles].map(css => `<link rel="stylesheet" href="/${css}">`).join('') + '</head>').replace('<div id="app"></div>', `<div id="app">${html}</div>`)
    .replace(/<title[^>]*>.*?<\/title>/, `<title>${escape(meta.title)}</title>`)
  for (const [id, value] of Object.entries({ 'meta-description':meta.description, 'meta-og-title':meta.title, 'meta-og-description':meta.description, 'meta-og-url':meta.canonical, 'meta-twitter-title':meta.title, 'meta-twitter-description':meta.description })) {
    page = page.replace(new RegExp(`(<meta\\s+id="${id}"[^>]*content=")[^"]*`), `$1${escape(value)}`)
  }
  page = page.replace(/(<link id="canonical-link"[^>]*href=")[^"]*/, `$1${escape(meta.canonical)}`)
  if (missing) page = page.replace('content="index, follow"', 'content="noindex, follow"').replace(/<link id="canonical-link"[^>]*>/, '')
  if (route === '/') {
    const schema = { '@context':'https://schema.org', '@type':'WebSite', name:'SanitiseAI', alternateName:'Sanitise AI', url:'https://sanitiseai.com/' }
    page = page.replace('</head>', `<script type="application/ld+json" data-page-schema>${JSON.stringify(schema)}</script></head>`)
  }
  const file = missing ? 'dist/404.html' : route === '/' ? 'dist/index.html' : `dist${route}.html`
  await mkdir(file.slice(0, file.lastIndexOf('/')), { recursive:true })
  await writeFile(file, page)
  console.log(`Rendered ${route}`)
}

await writeFile('dist/_redirects', routes.filter(route => route !== '/').map(route => `${route} ${route}.html 200\n${route}/ ${route} 301!`).join('\n') + '\n')
