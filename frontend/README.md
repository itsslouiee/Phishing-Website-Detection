# Phishing Website Detector (frontend)

A Next.js frontend for a machine learning phishing URL detector. Paste a URL, get the XGBoost prediction, then compare what XGBoost, Random Forest and Logistic Regression each predicted for that same URL alongside their overall evaluation metrics.

This repository contains the frontend only. The FastAPI backend is implemented separately and must follow [`API_CONTRACT.md`](./API_CONTRACT.md).

## Stack

Next.js (App Router), React, TypeScript, Tailwind CSS v4, Lucide icons, Zod (runtime validation of API responses).

## Getting started

Requires Node.js 20+ and pnpm.

```bash
pnpm install
cp .env.example .env.local   # then fill in the values
pnpm dev
```

Open http://localhost:3000.

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | FastAPI base URL, no trailing slash (for example `http://localhost:8000`). |
| `NEXT_PUBLIC_GITHUB_URL` | Your repository URL. The header icon is hidden if this is empty or invalid. |

`NEXT_PUBLIC_*` values are baked in at build time, so restart `pnpm dev` (or rebuild) after changing them.

## Scripts

```bash
pnpm dev         # development server
pnpm typecheck   # tsc --noEmit
pnpm lint        # eslint
pnpm build       # production build
pnpm start       # serve the production build
```

## Page structure (fixed order)

1. **Header**: project name and GitHub icon.
2. **URL analysis**: input, `Analyze URL`, and the XGBoost result with its phishing probability gauge.
3. **Model evaluation**: per-URL predictions from all three models (with an agreement summary) and the overall metrics comparison and confusion matrices. Everything is visible by default; there are no tabs, dropdowns or compare buttons.
4. **Workflow**: URL Input → Feature Extraction → Model Inference → Prediction.
5. **Footer**.

## How it behaves

- Nothing is hardcoded or simulated. All metrics, predictions and probabilities come from the API.
- If the API address is missing or the backend is down, the page stays usable and shows a clear error with a retry button where it makes sense. It never shows made-up results.
- One click on **Analyze URL** sends `/predict` and `/compare` in parallel. The main result shows as soon as `/predict` returns; the comparison fills in when `/compare` returns. Starting a new analysis cancels any request still in flight, so old results cannot overwrite new ones.
- Evaluation metrics load on page load, independently of any URL.

## Project layout

```
app/                 layout, global styles (design tokens + animations), page
components/          UI sections and small building blocks
hooks/               data hooks (analysis flow, evaluation, health)
lib/                 API client, response schemas, config, helpers
API_CONTRACT.md      endpoints and response schemas for the backend
```

API calls live only in `lib/api.ts`; components never call `fetch` directly.
