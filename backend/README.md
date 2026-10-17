# Phishing Detection Backend

FastAPI service that serves your trained scikit-learn phishing classifiers to the Next.js frontend in `frontend/`.

## What is and isn't supported

| Capability | Status |
|---|---|
| Feature-based prediction (`POST /api/predict`) | **Implemented and tested** (synthetic models only; no real model of yours has been run yet) |
| Health / models / features metadata | Implemented |
| URL-based analysis (`POST /api/analyze`, what the frontend calls) | **Route and contract implemented, but returns 501 until you plug in a feature extractor** |
| Prediction history, database, auth | Not implemented (the frontend has no history UI) |
| `GET /evaluation` (frontend metrics section) | Not implemented: no verified metrics exist yet |

**Feature-based vs URL-based:** feature-based means the client already has the model's input features. URL-based means the server must turn a URL into those exact features first. Your earlier models used content-based (HTML) features, so a URL can only be analysed with an extractor that reproduces your training pipeline exactly. None exists in this backend, and it will not guess one.

## Layout

```
backend/
  app/
    main.py                  app factory, CORS, size limit, error handlers
    config.py                env-based settings
    schemas.py               Pydantic request/response contract
    errors.py                client-safe errors
    api/routes.py            endpoints
    services/model_registry.py   artifact loading + validation (once, at startup)
    services/inference.py        input validation + prediction
    services/extractor.py        documented hook for URL -> features
  tests/                     pytest suite (synthetic fixtures, no network)
```

## Artifact contract (`models/` at the repo root)

Put these in `models/` (or point `PHISH_MODELS_DIR` elsewhere):

- `metadata.json` (required):

```json
{
  "feature_columns": ["..."],
  "label_mapping": {"0": "legitimate", "1": "phishing"},
  "best_model": "Random Forest",
  "models": {"Random Forest": "random_forest.joblib", "SVM": "svm.joblib"}
}
```

- Each model file is a fitted estimator, **preferably a full `sklearn.pipeline.Pipeline`** (scaler + model) so preprocessing is applied identically at inference. Preprocessing is never refit.
- `label_mapping` is required because only your dataset knows whether `1` means phishing. The loader refuses to start without it.
- Legacy files `all_models.pkl`, `feature_columns.pkl`, `best_model_name.pkl` are also accepted instead of the matching `metadata.json` keys, but `metadata.json` with `label_mapping` is still required.

Add something like this at the end of your `train_model.py` (it only writes files; it does not retrain anything by itself):

```python
import json, joblib
joblib.dump(best_pipeline, "models/random_forest.joblib")   # one per model
json.dump({
    "feature_columns": list(X_train.columns),
    "label_mapping": {"0": "legitimate", "1": "phishing"},   # VERIFY against your dataset
    "best_model": "Random Forest",                           # chosen from YOUR evaluation
    "models": {"Random Forest": "random_forest.joblib"},
}, open("models/metadata.json", "w"), indent=2)
```

At startup the loader checks: every model has `predict`, the feature order/count the model remembers (`feature_names_in_`, `n_features_in_`) matches `feature_columns`, every class the model can output exists in `label_mapping`, and the best model is among those loaded. If anything fails, the API still starts but `/api/health` reports `ready: false` and prediction endpoints return 503. Details are logged server-side only.

## Inference lifecycle

1. Models load once at startup.
2. Request body is schema-validated (strict types: `"1"` is rejected, not coerced).
3. `build_row` rejects missing/unexpected features and non-finite numbers. Nothing is imputed.
4. Values are placed in training column order in a DataFrame.
5. `predict` runs; the raw class is mapped through `label_mapping`.
6. `probabilities` are returned only if the model really has `predict_proba` (e.g. an `SVC` without `probability=True` returns none). Confidence in `/analyze` is the probability of the predicted class and is omitted when unavailable. A probability is not an explanation.

## Endpoints

| Method | Path | Notes |
|---|---|---|
| GET | `/api/health` | `{status, ready, detail}` |
| GET | `/api/models` | names, default, `supports_probabilities` |
| GET | `/api/features` | verified feature names in order, label mapping |
| POST | `/api/predict` | `{"features": {...}, "model"?: "..."}` |
| POST | `/api/analyze` | frontend contract `{url, mode, model?}` (501 without an extractor; `compare` mode returns 422) |

Swagger UI: `http://localhost:8000/docs`.

```bash
curl -s localhost:8000/api/health
curl -s localhost:8000/api/features
curl -s -X POST localhost:8000/api/predict -H 'Content-Type: application/json' \
  -d '{"features": {"<name from /api/features>": 1, "...": 0}}'
```

Success response (`probabilities` omitted when unavailable):

```json
{"prediction": "phishing", "is_phishing": true, "model": "Random Forest",
 "probabilities": {"legitimate": 0.08, "phishing": 0.92}}
```

Errors are `{"detail": "..."}`: 404 unknown model, 413 body too large, 422 invalid input (the submitted values are never echoed back), 501 no extractor, 502 extraction failed, 503 not ready, 500 generic.

## Setup on Kali (separate venv, no sudo, no global installs)

```bash
cd Phising-Website-Detection/backend
python3 -m venv .venv-backend          # not your existing .venv / venv
source .venv-backend/bin/activate
pip install -r requirements.txt
cp .env.example .env                   # optional; values are read from real env vars
uvicorn app.main:app --reload --port 8000
```

Env vars are read from the process environment (`.env` is a reference file, not auto-loaded), e.g. `PHISH_CORS_ORIGINS=http://localhost:3000 uvicorn app.main:app --port 8000`.

Tests (no internet, no dataset):

```bash
pytest -q
```

Add `.venv-backend/` to `.gitignore`.

## Connecting the frontend

In `frontend/.env.local`:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_DEMO_MODE=false
```

The frontend currently calls `/analyze`, `/models`, `/evaluation` relative to that base, which map to `/api/analyze` and `/api/models`. That works with **no frontend code change**. Until an extractor exists, analyses will show the frontend's generic "service unavailable" error (the backend's 501 explains why). CORS only allows `http://localhost:3000`; the deployed Vercel site cannot reach a backend on your laptop, and you should add its origin to `PHISH_CORS_ORIGINS` only once the backend is hosted somewhere reachable.

## Security notes and limits

- Pickle/joblib files can execute code on load; only files in the local `models/` directory are loaded, names cannot escape it, and users can never upload models.
- Strict schemas, a body-size cap (Content-Length based; add a proxy limit when deployed), narrow CORS, generic client errors, no input logging.
- No SSRF surface today because the server never fetches URLs. If you add an extractor that fetches pages, it must block private/loopback/link-local addresses, re-validate every redirect, resist DNS rebinding, and enforce timeouts and size/content-type limits.
- No authentication or rate limiting. Add both before exposing this publicly. This has had no security assessment.
- Nothing here validates your models' accuracy; metrics will come from your own evaluation.
