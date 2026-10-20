# Phishing Website Detection

A polished Next.js frontend for a machine-learning-powered phishing website detection platform.

## Prerequisites

- Node.js 20+
- pnpm 12+
- A FastAPI service (optional while demo mode is enabled)

## Local development

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

Open http://localhost:3000.

## Environment

`NEXT_PUBLIC_DEMO_MODE=true` keeps the analyzer in visibly labeled demo mode. Set it to `false` and provide `NEXT_PUBLIC_API_BASE_URL` when the FastAPI service is ready.

The API service layer currently maps these endpoints:

- `POST /analyze` — URL analysis
- `GET /models` — available backend models
- `GET /evaluation` — verified evaluation metrics

Confirm the best model, selectable models and verified evaluation metrics in `lib/config.ts` (currently empty on purpose: no values are invented).

Update `lib/api.ts` as the final FastAPI response schemas are agreed.

## Production build

```bash
pnpm build
pnpm start
```

No authentication, database, Docker, or secrets are required by this frontend.
