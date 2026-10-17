"""Loads trained artifacts once at startup and validates them.

Artifact contract (all inside PHISH_MODELS_DIR, which you control):

  metadata.json   REQUIRED. Must contain "label_mapping", e.g.
                  {"0": "legitimate", "1": "phishing"}. We never guess which class
                  is phishing: that depends on how your dataset was encoded.
                  Optional keys: "feature_columns", "best_model", "models"
                  ({"Display Name": "file.joblib"}).
  Models          either listed in metadata["models"], or a legacy all_models.pkl
                  (dict: name -> fitted estimator/pipeline).
  Feature columns metadata["feature_columns"] or legacy feature_columns.pkl.
  Best model      metadata["best_model"] or legacy best_model_name.pkl.

joblib/pickle files can execute code when loaded, so only files from this
trusted local directory are ever loaded; users can never upload or name one.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from app.errors import ArtifactError

logger = logging.getLogger("phishguard.registry")

PHISHING = "phishing"
LEGITIMATE = "legitimate"


@dataclass(frozen=True)
class ModelBundle:
    feature_columns: list[str]
    label_mapping: dict[str, str]  # str(class value) -> "legitimate" | "phishing"
    models: dict[str, Any]
    best_model: str


def class_key(value: Any) -> str:
    """Normalise a class value (numpy int, 1.0, "1") to a stable string key."""
    try:
        as_float = float(value)
        if as_float.is_integer():
            return str(int(as_float))
    except (TypeError, ValueError):
        pass
    return str(value)


def _load_file(models_dir: Path, filename: str) -> Any:
    # Only plain file names inside models_dir: blocks "../" style traversal
    # even though metadata.json is trusted.
    path = (models_dir / filename).resolve()
    if path.parent != models_dir.resolve():
        raise ArtifactError(f"artifact name {filename!r} escapes the models directory")
    if not path.is_file():
        raise ArtifactError(f"missing artifact file: {filename}")
    return joblib.load(path)


def _read_metadata(models_dir: Path) -> dict:
    path = models_dir / "metadata.json"
    if not path.is_file():
        raise ArtifactError("metadata.json not found (it must define label_mapping)")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactError(f"metadata.json is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ArtifactError("metadata.json must contain a JSON object")
    return data


def _validate_label_mapping(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict) or not raw:
        raise ArtifactError("metadata.json: label_mapping is required")
    mapping = {class_key(k): v for k, v in raw.items()}
    if set(mapping.values()) != {PHISHING, LEGITIMATE}:
        raise ArtifactError('label_mapping values must be exactly "legitimate" and "phishing"')
    return mapping


def _load_feature_columns(models_dir: Path, meta: dict) -> list[str]:
    columns = meta.get("feature_columns")
    if columns is None:
        columns = list(_load_file(models_dir, "feature_columns.pkl"))
    if not columns or not all(isinstance(c, str) for c in columns):
        raise ArtifactError("feature columns must be a non-empty list of strings")
    if len(set(columns)) != len(columns):
        raise ArtifactError("feature columns contain duplicates")
    return list(columns)


def _load_models(models_dir: Path, meta: dict) -> dict[str, Any]:
    listed = meta.get("models")
    if listed:
        return {name: _load_file(models_dir, filename) for name, filename in listed.items()}
    models = _load_file(models_dir, "all_models.pkl")
    if not isinstance(models, dict) or not models:
        raise ArtifactError("all_models.pkl must be a non-empty dict of name -> model")
    return models


def _validate_model(name: str, model: Any, columns: list[str], mapping: dict[str, str]) -> None:
    if not hasattr(model, "predict"):
        raise ArtifactError(f"model {name!r} has no predict()")
    # Feature ORDER matters: sklearn estimators are positional. If the model was
    # fitted on a DataFrame it remembers the training column order; it must match.
    names = getattr(model, "feature_names_in_", None)
    if names is not None and list(names) != columns:
        raise ArtifactError(f"model {name!r} was trained on a different feature order")
    n_features = getattr(model, "n_features_in_", None)
    if n_features is not None and n_features != len(columns):
        raise ArtifactError(f"model {name!r} expects {n_features} features, not {len(columns)}")
    for cls in getattr(model, "classes_", []):
        if class_key(cls) not in mapping:
            raise ArtifactError(f"model {name!r} predicts class {cls!r} missing from label_mapping")


def load_bundle(models_dir: Path) -> ModelBundle:
    if not models_dir.is_dir():
        raise ArtifactError("models directory does not exist")
    meta = _read_metadata(models_dir)
    mapping = _validate_label_mapping(meta.get("label_mapping"))
    columns = _load_feature_columns(models_dir, meta)
    models = _load_models(models_dir, meta)
    for name, model in models.items():
        _validate_model(name, model, columns, mapping)
    best = meta.get("best_model") or str(_load_file(models_dir, "best_model_name.pkl"))
    if best not in models:
        raise ArtifactError(f"best model {best!r} is not among the loaded models")
    return ModelBundle(columns, mapping, models, best)
