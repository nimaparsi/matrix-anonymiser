# Matrix Anonymiser (Vue + Netlify Functions)

Standalone anonymisation MVP with matrix-style UI, freemium caps, and Stripe-ready pro token flow.

## Stack
- Frontend: Vue 3 + Vite
- Backend: Netlify Functions (Node)
- Detection: Regex + lightweight heuristics (PERSON/ORG/ADDRESS/date patterns)
- File input: upload `.pdf` or text files (`.txt`, `.md`, `.csv`, `.json`, `.log`) and load extracted text into the editor
- Limits: Upstash Redis REST (optional) with in-memory fallback

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

## Run locally (recommended)
1. Install Netlify CLI (once)
```bash
npm install -g netlify-cli
```

2. Start local full stack
```bash
netlify dev
```

App runs at `http://localhost:8888` with frontend + functions together.

## API endpoints
- `GET /api/health`
- `POST /api/anonymize`
- `POST /api/billing/create-checkout`
- `GET /api/billing/activate?session_id=...`
- `POST /api/billing/dev-upgrade` (non-production only)

## Netlify environment variables
Required:
- `USAGE_SALT`
- `JWT_SECRET`

Recommended:
- `FREE_DAILY_LIMIT=100`
- `PRO_DAILY_LIMIT=500`
- `MAX_INPUT_CHARS=50000`
- `PRO_TOKEN_DAYS=30`
- `COOKIE_SECURE=true`

Optional (Upstash):
- `REDIS_REST_URL`
- `REDIS_REST_TOKEN`

Optional (Stripe):
- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_ID`

Optional abuse control:
- `BOT_CHALLENGE_THRESHOLD=20`
- `BOT_CHALLENGE_SECRET=<secret>`

Optional external API override:
- `VITE_API_BASE=https://your-api.example.com`
(Default is same-origin `/api/*`.)

## Deploy to Netlify
1. Connect GitHub repo in Netlify.
2. Netlify auto-reads `netlify.toml`.
3. Add env vars above in Netlify UI.
4. Trigger deploy.

## Notes
- Text is processed transiently and not persisted by app logic.
- PDF/text file parsing is done in-browser before anonymisation request.
- This Netlify-only mode prioritizes speed/reliability over heavy NLP models.
- For higher NER accuracy later, add external NLP service as optional fallback.

## Native iOS App
- Native SwiftUI app + Share Extension scaffold lives in `ios/MatrixAnonymiser`.
- See `ios/MatrixAnonymiser/README.md` for setup and Xcode project generation.
