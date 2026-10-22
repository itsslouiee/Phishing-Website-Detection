# Phishing URL API (backend)

FastAPI service implementing `API_CONTRACT.md`. It only **reuses** the existing project
(nothing is copied or modified):

| Used from the project root | For |
| --- | --- |
| `models/xgboost.pkl`, `random_forest.pkl`, `logistic_regression.pkl` | predictions |
| `models/feature_columns.pkl` | feature order used in training |
| `feature_extraction/extractor.py` (`url_to_features`) | URL -> 70 features |
| `results_summary.csv` | `GET /api/v1/evaluation` |

## Layout
```
backend/
  app/main.py           routes, CORS, error envelope
  app/model_service.py  URL validation, model loading, scoring
  app/eval_results.py   reads results_summary.csv
  app/schemas.py        response models (from the contract)
  app/config.py         paths + settings
  tests/test_api.py     contract tests (real models, no mocks)
```
Place `backend/` next to `models/` and `feature_extraction/` (inside the project root).

## Run
```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```
Then use the `curl` commands at the bottom of `API_CONTRACT.md`. Tests: `pip install pytest httpx && pytest`.

## Settings (environment variables, all optional)
- `CORS_ORIGINS` – allowed frontend origin(s), comma-separated. Default `http://localhost:3000`.
- `PROJECT_ROOT` – project root if `backend/` is not directly inside it. Default: parent of `backend/`.

## Behaviour you should know about
- **The page is never fetched.** Only the URL text is analysed; the HTML-based features are
  computed from an empty page (the extractor's default). This keeps the server safe (no
  server-side requests to user-supplied URLs) but means predictions are not identical to what
  the models saw in training, where real HTML was available. See the notes delivered with this zip.
- **Evaluation** numbers are the 5-fold cross-validation means in `results_summary.csv`.
  `roc_auc`, `confusion_matrix` and `evaluation_samples` are not stored anywhere, so they are `null`.
- `label` is `phishing` when probability >= 0.5 (same rule for all three models).
- Models are `.pkl` files (pickle): only load files you trained yourself.
- Not included: auth, rate limiting, request-body size limits. Put the API behind a reverse
  proxy that provides them before exposing it publicly.
