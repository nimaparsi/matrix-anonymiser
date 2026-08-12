# SanitiseAI (Vue + Netlify Functions)

SanitiseAI is a web app for anonymising sensitive text before it is shared with AI tools, documents, support workflows, and downstream systems.

## Stack
- Frontend: Vue 3 + Vite
- Backend: Netlify Functions (Node)
- Detection: server-side anonymisation API with pattern and context-aware sensitive-data handling
- File input: upload `.pdf` or text files (`.txt`, `.md`, `.csv`, `.json`, `.log`) and load extracted text into the editor
- Contact: Netlify Function delivery via Resend, with optional relay override

## Versioning
- Repo version source of truth: [`VERSION`](./VERSION)
- Changelog: [`CHANGELOG.md`](./CHANGELOG.md)
- Frontend package version is kept in `frontend/package.json` and should match `VERSION`.

Release flow:
1. Bump repo version in `VERSION` (semantic versioning).
2. Bump frontend version:
```bash
cd frontend && npm version <major|minor|patch|x.y.z> --no-git-tag-version
```
3. Add release notes to `CHANGELOG.md`.
4. Commit and tag:
```bash
git add VERSION CHANGELOG.md frontend/package.json frontend/package-lock.json
git commit -m "release: v$(cat VERSION)"
git tag "v$(cat VERSION)"
git push origin main --tags
```

## Run locally
1. Install Netlify CLI once:
```bash
npm install -g netlify-cli
```

2. Start local full stack:
```bash
netlify dev
```

The app runs at `http://localhost:8888` with frontend and functions together.

## API endpoints
- `GET /api/health`
- `POST /api/anonymize`
- `POST /api/contact`

## Netlify environment variables
Required for production contact delivery:
- `RESEND_API_KEY`
- `CONTACT_TO_EMAIL`

Recommended:
- `CONTACT_FROM_EMAIL=SanitiseAI Contact <onboarding@resend.dev>` until the production sending domain is verified
- `USAGE_SALT`
- `JWT_SECRET`
- `FREE_DAILY_LIMIT=100`
- `MAX_INPUT_CHARS=50000`
- `COOKIE_SECURE=true`

Optional:
- `CONTACT_RELAY_URL` for a separate contact delivery backend
- `REDIS_REST_URL`
- `REDIS_REST_TOKEN`
- `VITE_API_BASE=https://your-api.example.com` (default is same-origin `/api/*`)
- `VITE_CHROME_EXTENSION_URL=https://chromewebstore.google.com/detail/...` once the extension listing is live

## Deploy to Netlify
1. Connect the GitHub repo in Netlify.
2. Netlify auto-reads `netlify.toml`.
3. Add production environment variables in Netlify UI.
4. Trigger deploy.

## Privacy notes
- Text is sent to the sanitisation API over HTTPS for processing.
- Raw input is not stored as prompt content by app logic.
- PDF/text file parsing is done in-browser before the anonymisation request.
- Users should review the sanitised output before sharing it with downstream tools.

## Chrome extension
The Chrome extension source lives in `chrome-extension/`. It uses `https://sanitiseai.com/api/anonymize` and is prepared for Chrome Web Store packaging. See `chrome-extension/README.md` and `chrome-extension/CHROME_WEB_STORE_CHECKLIST.md`.
