from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import Settings
from app.errors import AppError, ArtifactError
from app.schemas import FeatureExtractor
from app.services.model_registry import load_bundle

logger = logging.getLogger("phishguard")


def create_app(settings: Settings | None = None, extractor: FeatureExtractor | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load once. A failure leaves the API up with ready=false so /api/health
        # explains the state instead of the process crashing.
        app.state.bundle = None
        try:
            app.state.bundle = load_bundle(settings.models_dir)
            logger.info("Loaded %d model(s)", len(app.state.bundle.models))
        except ArtifactError as exc:
            logger.error("Model artifacts not loaded: %s (dir=%s)", exc, settings.models_dir)
        except Exception:
            logger.exception("Unexpected error while loading artifacts")
        yield

    app = FastAPI(title="Phishing Website Detection API", version="0.1.0", lifespan=lifespan)
    app.state.bundle = None
    app.state.extractor = extractor

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.middleware("http")
    async def limit_body_size(request: Request, call_next):
        # Content-Length check; reverse proxies should also enforce a hard limit.
        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > settings.max_body_bytes:
            return JSONResponse({"detail": "Request body too large"}, status_code=413)
        return await call_next(request)

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse({"detail": exc.message}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        # Report where/why, but never echo the submitted values back.
        errors = [{"loc": [str(p) for p in e["loc"]], "msg": e["msg"]} for e in exc.errors()]
        return JSONResponse({"detail": "Invalid request", "errors": errors}, status_code=422)

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception):
        logger.exception("Unhandled error")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    app.include_router(router)
    return app


app = create_app()
