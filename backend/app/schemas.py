from __future__ import annotations

from typing import Callable, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, field_validator

# Strict types: the string "1" is rejected instead of silently coerced.
FeatureValue = StrictInt | StrictFloat | StrictBool

# A feature extractor turns a URL into {feature_name: value}. See services/extractor.py.
FeatureExtractor = Callable[[str], dict]


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    features: dict[str, FeatureValue] = Field(..., max_length=1000)
    model: Optional[str] = Field(None, max_length=100, description="Defaults to the best model")


class PredictResponse(BaseModel):
    prediction: Literal["legitimate", "phishing"]
    is_phishing: bool
    model: str
    probabilities: Optional[dict[str, float]] = Field(
        None, description="Present only when the model genuinely provides probabilities"
    )


class AnalyzeRequest(BaseModel):
    """Matches the frontend's AnalyzeRequest in lib/api.ts."""

    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., max_length=2048)
    mode: Literal["best", "specific", "compare"] = "best"
    model: Optional[str] = Field(None, max_length=100)

    @field_validator("url")
    @classmethod
    def _http_url_only(cls, value: str) -> str:
        value = value.strip()
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("url must be an http:// or https:// URL")
        return value


class AnalyzeResponse(BaseModel):
    """Field names match what the frontend's ResultCard reads."""

    verdict: Literal["legitimate", "phishing"]
    confidence: Optional[float] = Field(
        None, description="Probability of the predicted class; only if the model provides one"
    )
    modelName: str
    status: str


class HealthResponse(BaseModel):
    status: str
    ready: bool
    detail: Optional[str] = None


class ModelInfo(BaseModel):
    name: str
    is_default: bool
    supports_probabilities: bool


class ModelsResponse(BaseModel):
    default: str
    models: list[ModelInfo]


class FeatureInfo(BaseModel):
    name: str
    type: Literal["number"] = "number"


class FeaturesResponse(BaseModel):
    count: int
    features: list[FeatureInfo]
    labels: dict[str, str]
