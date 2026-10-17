class AppError(Exception):
    status_code = 500
    message = "Internal server error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        self.message = message or self.message


class InputError(AppError):
    status_code = 422
    message = "Invalid input"


class ModelNotFoundError(AppError):
    status_code = 404
    message = "Unknown model"


class NotReadyError(AppError):
    status_code = 503
    message = "Model artifacts are not loaded; the inference service is not ready"


class ExtractorUnavailableError(AppError):
    status_code = 501
    message = (
        "URL analysis is not available: no feature extractor compatible with the "
        "trained model is configured. Use POST /api/predict with extracted features."
    )


class ExtractionError(AppError):
    status_code = 502
    message = "Could not extract features from the URL"


class InferenceError(AppError):
    status_code = 500
    message = "Prediction failed"


class ArtifactError(Exception):
    """Raised while loading artifacts at startup. Logged server-side only."""
