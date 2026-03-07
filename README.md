# Matrix Anonymiser (Vue + FastAPI)

Standalone anonymisation MVP with matrix-style UI, freemium caps, and Stripe-ready pro token flow.

## Stack
- Frontend: Vue 3 + Vite
- Backend: FastAPI
- Detection: Regex + optional Presidio NLP
- Limits: Redis (Upstash-compatible) with in-memory fallback

## Run locally
1. Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

2. Frontend (new terminal)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## API
- `GET /api/health`
- `POST /api/anonymize`
- `POST /api/billing/create-checkout`
- `GET /api/billing/activate?session_id=...`
- `POST /api/billing/dev-upgrade` (non-production only)

## Notes
- Text is processed transiently and not persisted by app logic.
- Presidio/spaCy are optional; regex detection still works if NLP dependencies are unavailable.
- For production, set secure secrets and enable HTTPS + `COOKIE_SECURE=true`.

## Deploy (Netlify + Render)
1. Deploy backend on Render
```bash
# from project root
render blueprint apply
```
Or create a Render Web Service manually:
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/health`

Set env vars on Render (required):
- `ENV=production`
- `FRONTEND_ORIGIN=https://<your-netlify-site>.netlify.app`
- `USAGE_SALT`, `JWT_SECRET`
- `REDIS_URL` (Upstash recommended)
- `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID` (if billing enabled)
- `COOKIE_SECURE=true`

2. Deploy frontend on Netlify
- Netlify detects `netlify.toml` in repo root.
- Build base: `frontend`
- Build command: `npm run build`
- Publish dir: `dist`

Set env var on Netlify:
- `VITE_API_BASE=https://<your-render-service>.onrender.com`

3. Validate production
- Open your Netlify URL.
- Check backend health at `https://<your-render-service>.onrender.com/api/health`.
- Run an anonymization request from the UI.
