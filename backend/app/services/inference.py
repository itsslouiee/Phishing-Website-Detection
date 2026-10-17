"""Validation + prediction on top of a loaded ModelBundle."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.errors import InferenceError, InputError, ModelNotFoundError
from app.services.model_registry import PHISHING, ModelBundle, class_key

logger = logging.getLogger("phishguard.inference")


@dataclass(frozen=True)
class Prediction:
    prediction: str
    is_phishing: bool
    model: str
    probabilities: dict[str, float] | None


def supports_probabilities(model: Any) -> bool:
    return callable(getattr(model, "predict_proba", None)) and hasattr(model, "classes_")


def resolve_model(bundle: ModelBundle, name: str | None) -> tuple[str, Any]:
    chosen = name or bundle.best_model
    if chosen not in bundle.models:
        raise ModelNotFoundError(f"Unknown model: {chosen[:60]!r}")
    return chosen, bundle.models[chosen]


def build_row(bundle: ModelBundle, features: dict[str, Any]) -> pd.DataFrame:
    """Check completeness/types and order values exactly like training.

    Nothing is imputed: a missing or bad value is rejected, never filled in.
    """
    expected = bundle.feature_columns
    missing = [c for c in expected if c not in features]
    unexpected = [k for k in features if k not in expected]
    if missing or unexpected:
        parts = []
        if missing:
            parts.append(f"missing features: {missing[:10]}")
        if unexpected:
            parts.append(f"unexpected features: {[k[:40] for k in unexpected[:10]]}")
        raise InputError("; ".join(parts))
    for name in expected:
        value = features[name]
        if isinstance(value, bool):
            continue
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise InputError(f"feature {name!r} must be a finite number")
    # A DataFrame with explicit columns keeps the training order and, for
    # estimators fitted on DataFrames, the feature names sklearn checks.
    return pd.DataFrame([[float(features[c]) for c in expected]], columns=expected)


def _probabilities(bundle: ModelBundle, model: Any, row: pd.DataFrame) -> dict[str, float] | None:
    # Only report probabilities the model genuinely produces; never invent them.
    if not supports_probabilities(model):
        return None
    try:
        raw = model.predict_proba(row)[0]
    except Exception:  # e.g. SVC fitted without probability=True
        return None
    return {bundle.label_mapping[class_key(c)]: float(p) for c, p in zip(model.classes_, raw)}


def predict(bundle: ModelBundle, features: dict[str, Any], model_name: str | None = None) -> Prediction:
    name, model = resolve_model(bundle, model_name)
    row = build_row(bundle, features)
    try:
        raw_label = model.predict(row)[0]
        label = bundle.label_mapping[class_key(raw_label)]
        probabilities = _probabilities(bundle, model, row)
    except Exception as exc:
        # Log details server-side only; clients get a generic message.
        logger.exception("inference failed for model %s", name)
        raise InferenceError() from exc
    return Prediction(label, label == PHISHING, name, probabilities)
