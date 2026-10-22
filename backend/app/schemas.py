"""Request/response shapes. Copied from the reference sketch in API_CONTRACT.md."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

ModelId = Literal["xgboost", "random_forest", "logistic_regression"]
Label = Literal["phishing", "legitimate"]


class UrlRequest(BaseModel):
    # Length / scheme checks happen in validate_url() so the error message
    # can be short and readable for the user.
    url: str


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
