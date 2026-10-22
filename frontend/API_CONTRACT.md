# API Contract

This is the contract the frontend is written against. Implement the FastAPI backend to match it exactly. The frontend validates every response at runtime (see `lib/schemas.ts`); anything that does not match is shown as an error, never rendered.

## Conventions

- Base URL: set in the frontend as `NEXT_PUBLIC_API_BASE_URL` (no trailing slash).
- All bodies are JSON (`Content-Type: application/json`).
- Probabilities and metrics are **fractions between 0 and 1** (the UI formats them as percentages).
- **Positive class = phishing.** Precision, recall, F1 and the confusion matrix are all computed with phishing as the positive class.
- **CORS:** the browser calls the API directly, so enable CORS for the frontend origin (for example `http://localhost:3000`) with methods `GET, POST, OPTIONS` and header `Content-Type`.
- Models are identified by these ids: `xgboost`, `random_forest`, `logistic_regression`.
- Never return placeholder or estimated values. If something is not available, return `null` (where the schema allows it) or an error.

### Two terms that must not be confused

| Term | Meaning | Where it appears |
| --- | --- | --- |
| **Evaluation metrics** | Aggregate quality of a model, measured offline (ideally on a held-out test set). Independent of any submitted URL. | `GET /api/v1/evaluation` |
| **Phishing probability** | One model's score for **one submitted URL**: `P(phishing \| url)`, i.e. `predict_proba(...)[:, phishing_class_index]`. A model score, not a guarantee, and not necessarily calibrated. | `POST /api/v1/predict`, `POST /api/v1/compare` |

`label` must agree with `phishing_probability` at the model's decision threshold (normally 0.5): `"phishing"` when the probability is at or above the threshold, `"legitimate"` otherwise. If a model cannot produce a probability, return `null` for it and still return the label.

## How the frontend uses the endpoints

1. On load: `GET /health` (and again every 30 s) for the small status line, and `GET /api/v1/evaluation` for the overall metrics.
2. When the user clicks **Analyze URL**, it sends `POST /api/v1/predict` and `POST /api/v1/compare` **in parallel** for the same URL.
   - `/predict` fills the main XGBoost result as soon as it returns.
   - `/compare` fills the three per-URL predictions in the comparison section.
   - They settle independently, so a failure in one does not hide the other, and each has its own retry.

Both calls should return the same XGBoost label and probability for the same URL.

---

## `GET /health`

Reports whether the service is up and which models are loaded. **Always return HTTP 200** while the process is running; use `"degraded"` when a model is missing.

Response `200`:

```json
{
  "status": "ok",
  "models": {
    "xgboost": true,
    "random_forest": true,
    "logistic_regression": true
  }
}
```

| Field | Type | Notes |
| --- | --- | --- |
| `status` | `"ok"` \| `"degraded"` | `"ok"` only when all three models are loaded. |
| `models.<id>` | boolean | `true` when that model is loaded and ready. |

## `GET /api/v1/evaluation`

Overall evaluation metrics for all three models. Must work without any URL analysis having happened.

Response `200`:

```json
{
  "evaluation_samples": 11000,
  "models": [
    {
      "model": "xgboost",
      "metrics": { "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "roc_auc": 0.0 },
      "confusion_matrix": { "tn": 0, "fp": 0, "fn": 0, "tp": 0 }
    },
    { "model": "random_forest", "metrics": { "...": "..." }, "confusion_matrix": { "...": "..." } },
    { "model": "logistic_regression", "metrics": { "...": "..." }, "confusion_matrix": { "...": "..." } }
  ]
}
```

(All numbers above are format placeholders. Return the values you actually measured.)

| Field | Type | Notes |
| --- | --- | --- |
| `evaluation_samples` | integer, optional/`null` | Number of samples the metrics were computed on. |
| `models[].model` | model id | One entry per model. |
| `models[].metrics.accuracy` / `precision` / `recall` / `f1` | number 0–1 | Required. |
| `models[].metrics.roc_auc` | number 0–1 or `null` | Optional. The row is hidden if every model returns `null`. |
| `models[].confusion_matrix` | object or `null` | `tn`, `fp`, `fn`, `tp` as non-negative integers (phishing = positive). Optional. |

## `POST /api/v1/predict`

The main prediction, **always from XGBoost**.

Request:

```json
{ "url": "https://example.com" }
```

Response `200`:

```json
{
  "url": "https://example.com",
  "model": "xgboost",
  "label": "legitimate",
  "phishing_probability": 0.03
}
```

(`0.03` is only an example value.)

| Field | Type | Notes |
| --- | --- | --- |
| `url` | string | The URL that was analyzed (echo back what you scored). |
| `model` | `"xgboost"` | Always `xgboost`. |
| `label` | `"phishing"` \| `"legitimate"` | |
| `phishing_probability` | number 0–1 or `null` | `P(phishing)` as defined above. |

## `POST /api/v1/compare`

Predictions from all three models for the **same URL**.

Request: same as `/predict`.

Response `200`:

```json
{
  "url": "https://example.com",
  "predictions": [
    { "model": "xgboost", "label": "legitimate", "phishing_probability": 0.03 },
    { "model": "random_forest", "label": "legitimate", "phishing_probability": 0.05 },
    { "model": "logistic_regression", "label": "phishing", "phishing_probability": 0.61 }
  ]
}
```

(Example values only.) `predictions` must contain exactly one entry for each of the three model ids. A response missing any of them is rejected by the frontend.

## Errors

Return a non-2xx status with this envelope:

```json
{ "error": { "code": "invalid_url", "message": "Enter a valid http:// or https:// URL." } }
```

| Status | `code` | When |
| --- | --- | --- |
| `400` / `422` | `invalid_url` | Missing/empty URL, not http(s), too long (limit 2048 chars), unparseable. The `message` is shown to the user, so keep it short and readable. |
| `503` | `models_not_ready` | A required model is not loaded yet. |
| `500` | `internal_error` | Anything unexpected. |

FastAPI's default validation error body (`{"detail": [...]}`) does not match this envelope. Add an exception handler for `RequestValidationError` that returns it. If the envelope is missing, the frontend falls back to a generic message.

## Reference sketch (FastAPI + Pydantic)

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field

ModelId = Literal["xgboost", "random_forest", "logistic_regression"]
Label = Literal["phishing", "legitimate"]

class UrlRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

class Health(BaseModel):
    status: Literal["ok", "degraded"]
    models: dict[ModelId, bool]

class Metrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None

class ConfusionMatrix(BaseModel):
    tn: int
    fp: int
    fn: int
    tp: int

class ModelEvaluation(BaseModel):
    model: ModelId
    metrics: Metrics
    confusion_matrix: Optional[ConfusionMatrix] = None

class EvaluationResponse(BaseModel):
    evaluation_samples: Optional[int] = None
    models: list[ModelEvaluation]

class Prediction(BaseModel):
    model: ModelId
    label: Label
    phishing_probability: Optional[float] = Field(default=None, ge=0, le=1)

class PredictResponse(BaseModel):
    url: str
    model: Literal["xgboost"] = "xgboost"
    label: Label
    phishing_probability: Optional[float] = Field(default=None, ge=0, le=1)

class CompareResponse(BaseModel):
    url: str
    predictions: list[Prediction]
```

## Quick manual test

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/evaluation
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
```

## UI wording that assumes how your backend works

The workflow section says the URL is "turned into the numeric features the models were trained on". If your backend does something different (for example fetching the page, DNS or WHOIS lookups), update the copy in `components/workflow.tsx` so it stays accurate.
