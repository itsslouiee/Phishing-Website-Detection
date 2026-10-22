"""Evaluation numbers for GET /api/v1/evaluation.

Source: the project's existing results_summary.csv, written by train_model.py
(mean of 5-fold stratified cross-validation, phishing = positive class).
Values are served exactly as stored; nothing is computed or estimated here.

NOT in that file, therefore returned as null: roc_auc, confusion_matrix and
evaluation_samples.
"""
import csv

from . import config
from .schemas import EvaluationResponse, Metrics, ModelEvaluation

# model name used in results_summary.csv -> model id used by the API
_CSV_NAMES = {
    "XGBoost": "xgboost",
    "Random Forest": "random_forest",
    "Logistic Regression": "logistic_regression",
}
_ORDER = ("xgboost", "random_forest", "logistic_regression")


def load_evaluation() -> EvaluationResponse:
    rows = {}
    with open(config.RESULTS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            model_id = _CSV_NAMES.get(row["Model"].strip())
            if model_id:
                rows[model_id] = row

    missing = [m for m in _ORDER if m not in rows]
    if missing:
        raise ValueError(f"results_summary.csv has no row for: {', '.join(missing)}")

    models = [
        ModelEvaluation(
            model=m,
            metrics=Metrics(
                accuracy=float(rows[m]["Accuracy"]),
                precision=float(rows[m]["Precision"]),
                recall=float(rows[m]["Recall"]),
                f1=float(rows[m]["F1"]),
                roc_auc=None,
            ),
            confusion_matrix=None,
        )
        for m in _ORDER
    ]
    return EvaluationResponse(evaluation_samples=None, models=models)
