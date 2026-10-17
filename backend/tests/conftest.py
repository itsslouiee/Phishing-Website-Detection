"""Synthetic fixtures. These tiny models only exercise the plumbing; their
outputs are NOT evaluation results for your real models."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from app.config import Settings
from app.main import create_app

COLUMNS = ["f_a", "f_b", "f_c"]
HIGH = {"f_a": 0.95, "f_b": 0.5, "f_c": 0.5}  # label 1 in the training rule
LOW = {"f_a": 0.05, "f_b": 0.5, "f_c": 0.5}   # label 0


def _training_data() -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.random((300, 3)), columns=COLUMNS)
    y = (X["f_a"] > 0.5).astype(int).to_numpy()  # class 1 iff f_a is high
    return X, y


def write_artifacts(directory: Path, label_mapping: dict[str, str]) -> None:
    X, y = _training_data()
    forest = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
    svm = SVC(random_state=0).fit(X, y)  # no probability=True -> no predict_proba
    joblib.dump(forest, directory / "forest.joblib")
    joblib.dump(svm, directory / "svm.joblib")
    (directory / "metadata.json").write_text(json.dumps({
        "feature_columns": COLUMNS,
        "label_mapping": label_mapping,
        "best_model": "Random Forest",
        "models": {"Random Forest": "forest.joblib", "SVM": "svm.joblib"},
    }))


def make_client(directory: Path, extractor=None, **kwargs) -> TestClient:
    app = create_app(Settings(models_dir=directory), extractor=extractor)
    return TestClient(app, **kwargs)


@pytest.fixture
def models_dir(tmp_path) -> Path:
    write_artifacts(tmp_path, {"0": "legitimate", "1": "phishing"})
    return tmp_path


@pytest.fixture
def client(models_dir):
    with make_client(models_dir) as c:
        yield c
