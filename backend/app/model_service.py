"""Loads the trained models and scores URLs.

Reuses, unchanged, from the project root:
  models/{xgboost,random_forest,logistic_regression}.pkl   trained models
  models/feature_columns.pkl                               feature order used in training
  feature_extraction/extractor.py                          url_to_features()
"""
import logging
import sys
from urllib.parse import urlsplit

import joblib
import pandas as pd

from . import config
from .schemas import Prediction

log = logging.getLogger("phishing-api")

# Make the existing `feature_extraction` package importable. Appended (not
# inserted first) so the project's own top-level scripts can never shadow ours.
if str(config.PROJECT_ROOT) not in sys.path:
    sys.path.append(str(config.PROJECT_ROOT))

import tldextract  # noqa: E402

# The feature code calls tldextract.extract(). By default tldextract downloads
# the public-suffix list over the network on first use; use its bundled copy
# instead so the API makes no hidden outbound requests and writes no cache.
tldextract.tldextract.TLD_EXTRACTOR = tldextract.TLDExtract(
    cache_dir=None, suffix_list_urls=()
)

from feature_extraction.extractor import url_to_features  # noqa: E402

MODEL_IDS = ("xgboost", "random_forest", "logistic_regression")

_models: dict = {}
_columns: list[str] | None = None


class InvalidUrl(ValueError):
    """Raised with a short, user-readable message."""


class ModelsNotReady(RuntimeError):
    pass


def load_models() -> None:
    """Load whatever is available. A missing file only marks that model as not loaded."""
    global _columns
    _models.clear()
    _columns = None
    try:
        _columns = list(joblib.load(config.MODELS_DIR / "feature_columns.pkl"))
    except Exception:
        log.exception("Could not load feature_columns.pkl; no model can be used")
        return
    for model_id in MODEL_IDS:
        try:
            _models[model_id] = joblib.load(config.MODELS_DIR / f"{model_id}.pkl")
        except Exception:
            log.exception("Could not load model %s", model_id)


def loaded() -> dict[str, bool]:
    return {m: (m in _models and _columns is not None) for m in MODEL_IDS}


def validate_url(raw: str) -> str:
    """Return the cleaned URL or raise InvalidUrl."""
    url = (raw or "").strip()
    if not url:
        raise InvalidUrl("Enter a URL.")
    if len(url) > config.MAX_URL_LENGTH:
        raise InvalidUrl(f"URL is too long (limit {config.MAX_URL_LENGTH} characters).")
    if any(ord(c) < 32 or ord(c) == 127 for c in url):
        raise InvalidUrl("Enter a valid http:// or https:// URL.")
    try:
        parts = urlsplit(url)
        host = parts.hostname
        parts.port  # raises ValueError for a bad port
    except ValueError:
        raise InvalidUrl("Enter a valid http:// or https:// URL.")
    if parts.scheme.lower() not in ("http", "https") or not host:
        raise InvalidUrl("Enter a valid http:// or https:// URL.")
    return url


def _features(url: str) -> pd.DataFrame:
    # The page is never fetched, so HTML is empty (this is the extractor's
    # default). Columns are put in exactly the order used for training.
    feats = url_to_features(url)
    return pd.DataFrame([feats])[_columns].astype(float)


def _score(model_id: str, x: pd.DataFrame) -> Prediction:
    model = _models[model_id]
    classes = list(model.classes_)
    phishing_idx = classes.index(1)  # label 1 = phishing (see train_model.py)
    p = float(model.predict_proba(x)[0, phishing_idx])
    label = "phishing" if p >= config.DECISION_THRESHOLD else "legitimate"
    return Prediction(model=model_id, label=label, phishing_probability=p)


def predict(model_ids: tuple[str, ...], url: str) -> list[Prediction]:
    if not all(loaded()[m] for m in model_ids):
        raise ModelsNotReady()
    x = _features(url)
    return [_score(m, x) for m in model_ids]
