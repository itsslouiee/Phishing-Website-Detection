from __future__ import annotations

from fastapi import APIRouter, Request

from app.errors import ExtractionError, ExtractorUnavailableError, InputError, NotReadyError
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    FeatureInfo,
    FeaturesResponse,
    HealthResponse,
    ModelInfo,
    ModelsResponse,
    PredictRequest,
    PredictResponse,
)
from app.services import inference
from app.services.model_registry import ModelBundle

router = APIRouter(prefix="/api")


def _bundle(request: Request) -> ModelBundle:
    bundle = request.app.state.bundle
    if bundle is None:
        raise NotReadyError()
    return bundle


@router.get("/health", response_model=HealthResponse, tags=["meta"])
def health(request: Request) -> HealthResponse:
    ready = request.app.state.bundle is not None
    return HealthResponse(
        status="ok",
        ready=ready,
        detail=None if ready else "Model artifacts are not loaded",
    )


@router.get("/models", response_model=ModelsResponse, tags=["meta"])
def list_models(request: Request) -> ModelsResponse:
    bundle = _bundle(request)
    return ModelsResponse(
        default=bundle.best_model,
        models=[
            ModelInfo(
                name=name,
                is_default=name == bundle.best_model,
                supports_probabilities=inference.supports_probabilities(model),
            )
            for name, model in bundle.models.items()
        ],
    )


@router.get("/features", response_model=FeaturesResponse, tags=["meta"])
def list_features(request: Request) -> FeaturesResponse:
    bundle = _bundle(request)
    return FeaturesResponse(
        count=len(bundle.feature_columns),
        features=[FeatureInfo(name=n) for n in bundle.feature_columns],
        labels=bundle.label_mapping,
    )


@router.post("/predict", response_model=PredictResponse, response_model_exclude_none=True, tags=["predict"])
def predict(body: PredictRequest, request: Request) -> PredictResponse:
    """Feature-based prediction: the client supplies already-extracted features."""
    result = inference.predict(_bundle(request), body.features, body.model)
    return PredictResponse(**result.__dict__)


@router.post("/analyze", response_model=AnalyzeResponse, response_model_exclude_none=True, tags=["predict"])
def analyze(body: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    """URL-based analysis used by the frontend. Needs a configured feature extractor."""
    bundle = _bundle(request)
    extractor = request.app.state.extractor
    if extractor is None:
        raise ExtractorUnavailableError()
    if body.mode == "compare":
        raise InputError("mode 'compare' is not supported yet")
    if body.mode == "specific" and not body.model:
        raise InputError("mode 'specific' requires a model name")
    try:
        features = extractor(body.url)
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError() from exc
    result = inference.predict(bundle, features, body.model if body.mode == "specific" else None)
    confidence = result.probabilities[result.prediction] if result.probabilities else None
    return AnalyzeResponse(
        verdict=result.prediction,
        confidence=confidence,
        modelName=result.model,
        status="Analysis complete",
    )
