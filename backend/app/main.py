"""FastAPI app implementing API_CONTRACT.md."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config, eval_results, model_service
from .model_service import InvalidUrl, ModelsNotReady
from .schemas import (
    CompareResponse,
    EvaluationResponse,
    Health,
    PredictResponse,
    UrlRequest,
)

log = logging.getLogger("phishing-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.load_models()
    yield


app = FastAPI(title="Phishing URL API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ---- error envelope: {"error": {"code": ..., "message": ...}} -------------
def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@app.exception_handler(RequestValidationError)
async def _validation_error(request: Request, exc: RequestValidationError):
    return _error(422, "invalid_url", "Enter a valid http:// or https:// URL.")


@app.exception_handler(InvalidUrl)
async def _invalid_url(request: Request, exc: InvalidUrl):
    return _error(422, "invalid_url", str(exc))


@app.exception_handler(ModelsNotReady)
async def _not_ready(request: Request, exc: ModelsNotReady):
    return _error(503, "models_not_ready", "The models are not loaded yet.")


@app.exception_handler(Exception)
async def _unexpected(request: Request, exc: Exception):
    log.exception("Unhandled error")  # details stay in the server log only
    return _error(500, "internal_error", "Something went wrong on the server.")


# ---- endpoints --------------------------------------------------------------
# Plain `def` (not async): scoring is CPU-bound, so FastAPI runs it in a worker
# thread instead of blocking the event loop.
@app.get("/health", response_model=Health)
def health():
    models = model_service.loaded()
    return Health(status="ok" if all(models.values()) else "degraded", models=models)

@app.get("/")
def read_root():
    return {"message": "Phishing URL API is running. Docs at /docs"}


@app.get("/api/v1/evaluation", response_model=EvaluationResponse)
def evaluation():
    return eval_results.load_evaluation()


@app.post("/api/v1/predict", response_model=PredictResponse)
def predict(req: UrlRequest):
    url = model_service.validate_url(req.url)
    (p,) = model_service.predict(("xgboost",), url)
    return PredictResponse(url=url, label=p.label, phishing_probability=p.phishing_probability)


@app.post("/api/v1/compare", response_model=CompareResponse)
def compare(req: UrlRequest):
    url = model_service.validate_url(req.url)
    preds = model_service.predict(model_service.MODEL_IDS, url)
    return CompareResponse(url=url, predictions=preds)
