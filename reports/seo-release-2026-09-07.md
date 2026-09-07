# Existing-page SEO release

## Implemented
- Vue build-time rendering for all 13 sitemap URLs, with matching initial and client titles, descriptions and canonicals. No new keyword routes.
- Route-specific CSS included in initial HTML; existing UI hydrates into its interactive state.
- Explicit known-page rewrites and genuine 404 fallback; unknown use-case slugs cannot display another workflow.
- Consistent /tool links and obsolete demo query cleanup.
- Removed unrelated FAQ graph; homepage WebSite identity remains scoped to homepage.
- All six workflows linked from homepage and tool, with related links, synthetic before/after examples, practical steps and specific limitations.
- Historical benchmark results exposed on /security#evaluation with date, method, misses and scope. Not a certification or universal accuracy claim.
- Lazy routes and PDF loading. Removed global Google Analytics and AdSense scripts from document template; aggregate conversion tracking is not replaced in this release.
- Restored pinch zoom, single main landmark and visible-by-default homepage content.

## Verification
- TypeScript, eight unit tests and six engine-backed synthetic example assertions passed.
- Client and server builds and prerendering passed.
- Browser checks across 13 routes: raw/rendered metadata, hydration, mobile overflow, no-JS content/styles, internal links and interactive Try example.
- Local static-host fixture returned 404 for unknown paths and unknown use-case slugs. Production Netlify behaviour must be rechecked after deployment.
- Homepage did not download PDF code in the browser check.

Reproduce with `npm run build`, `npm run typecheck`, `npm test`, `node scripts/check-workflow-examples.mjs`, and `node scripts/check-rendered-pages.mjs`.

## After deployment
Inspect /, /tool and all six use cases in Search Console; compare rendered and fetched canonicals and request recrawls for changed pages. Check both an unknown root path and an unknown use-case path return HTTP 404. Resubmit the existing sitemap. Compare equal 28-day performance windows, not isolated rank observations.

Search visibility is not guaranteed by deployment. Backlinks, field performance, crawl selection and user demand remain outside these code checks. Chrome store publication and signed-in provider testing remain manual; see the extension checklist.

References: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics and https://docs.netlify.com/manage/routing/redirects/redirect-options/.
