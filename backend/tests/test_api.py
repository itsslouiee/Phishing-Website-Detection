from __future__ import annotations

import pytest

from app.errors import ExtractionError
from tests.conftest import COLUMNS, HIGH, LOW, make_client, write_artifacts


# ---- health / loading ------------------------------------------------------

def test_health_ready(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["ready"] is True


def test_missing_artifacts_start_not_ready(tmp_path):
    with make_client(tmp_path / "does-not-exist") as c:
        assert c.get("/api/health").json()["ready"] is False
        assert c.get("/api/models").status_code == 503
        assert c.post("/api/predict", json={"features": HIGH}).status_code == 503


def test_missing_label_mapping_is_rejected(tmp_path):
    write_artifacts(tmp_path, {"0": "legitimate", "1": "phishing"})
    (tmp_path / "metadata.json").write_text('{"feature_columns": ["f_a", "f_b", "f_c"]}')
    with make_client(tmp_path) as c:
        assert c.get("/api/health").json()["ready"] is False


def test_wrong_feature_order_is_rejected(tmp_path):
    write_artifacts(tmp_path, {"0": "legitimate", "1": "phishing"})
    import json
    meta = json.loads((tmp_path / "metadata.json").read_text())
    meta["feature_columns"] = ["f_c", "f_b", "f_a"]  # differs from training order
    (tmp_path / "metadata.json").write_text(json.dumps(meta))
    with make_client(tmp_path) as c:
        assert c.get("/api/health").json()["ready"] is False


def test_artifact_name_cannot_escape_models_dir(tmp_path):
    write_artifacts(tmp_path, {"0": "legitimate", "1": "phishing"})
    import json
    meta = json.loads((tmp_path / "metadata.json").read_text())
    meta["models"] = {"Evil": "../outside.joblib"}
    (tmp_path / "metadata.json").write_text(json.dumps(meta))
    with make_client(tmp_path) as c:
        assert c.get("/api/health").json()["ready"] is False


# ---- metadata endpoints ----------------------------------------------------

def test_models_and_probability_capability(client):
    body = client.get("/api/models").json()
    by_name = {m["name"]: m for m in body["models"]}
    assert body["default"] == "Random Forest"
    assert by_name["Random Forest"]["supports_probabilities"] is True
    assert by_name["SVM"]["supports_probabilities"] is False


def test_features_endpoint_exposes_names_only(client):
    body = client.get("/api/features").json()
    assert [f["name"] for f in body["features"]] == COLUMNS
    assert "/" not in str(body)  # no filesystem paths


# ---- prediction ------------------------------------------------------------

def test_valid_prediction_with_probabilities(client):
    body = client.post("/api/predict", json={"features": HIGH}).json()
    assert body["prediction"] == "phishing" and body["is_phishing"] is True
    assert body["model"] == "Random Forest"
    assert set(body["probabilities"]) == {"legitimate", "phishing"}
    assert abs(sum(body["probabilities"].values()) - 1.0) < 1e-6
    legit = client.post("/api/predict", json={"features": LOW}).json()
    assert legit["prediction"] == "legitimate" and legit["is_phishing"] is False


def test_model_without_probabilities_omits_them(client):
    body = client.post("/api/predict", json={"features": HIGH, "model": "SVM"}).json()
    assert body["prediction"] == "phishing"
    assert "probabilities" not in body


def test_label_mapping_is_taken_from_metadata(tmp_path):
    # Same trained models, but the dataset encoded phishing as 0.
    write_artifacts(tmp_path, {"0": "phishing", "1": "legitimate"})
    with make_client(tmp_path) as c:
        high = c.post("/api/predict", json={"features": HIGH}).json()  # class 1
        low = c.post("/api/predict", json={"features": LOW}).json()    # class 0
    assert high["prediction"] == "legitimate" and high["is_phishing"] is False
    assert low["prediction"] == "phishing" and low["is_phishing"] is True


def test_unknown_model_is_404(client):
    r = client.post("/api/predict", json={"features": HIGH, "model": "Nope"})
    assert r.status_code == 404


def test_missing_feature_rejected(client):
    r = client.post("/api/predict", json={"features": {"f_a": 0.5, "f_b": 0.5}})
    assert r.status_code == 422 and "f_c" in r.json()["detail"]


def test_unexpected_feature_rejected(client):
    r = client.post("/api/predict", json={"features": {**HIGH, "extra": 1}})
    assert r.status_code == 422


@pytest.mark.parametrize("bad", ["1", None, [1], {"x": 1}])
def test_wrongly_typed_value_rejected(client, bad):
    r = client.post("/api/predict", json={"features": {**HIGH, "f_a": bad}})
    assert r.status_code == 422


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_values_rejected(client, token):
    raw = '{"features": {"f_a": %s, "f_b": 0.5, "f_c": 0.5}}' % token
    r = client.post("/api/predict", content=raw, headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_validation_errors_do_not_echo_input(client):
    r = client.post("/api/predict", json={"features": {**HIGH, "f_a": "SECRET-VALUE"}})
    assert "SECRET-VALUE" not in r.text


def test_oversized_body_rejected(client):
    r = client.post("/api/predict", content=b"x" * 70_000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_inference_failure_returns_generic_500(models_dir, monkeypatch):
    with make_client(models_dir) as c:
        model = c.app.state.bundle.models["Random Forest"]
        monkeypatch.setattr(type(model), "predict", lambda self, X: (_ for _ in ()).throw(RuntimeError("secret /path")))
        r = c.post("/api/predict", json={"features": HIGH})
    assert r.status_code == 500
    assert r.json() == {"detail": "Prediction failed"}


# ---- /api/analyze (frontend contract) --------------------------------------

def test_analyze_without_extractor_is_501(client):
    r = client.post("/api/analyze", json={"url": "https://example.com", "mode": "best"})
    assert r.status_code == 501


@pytest.mark.parametrize("url", ["ftp://example.com", "javascript:alert(1)", "example.com", "http://"])
def test_analyze_rejects_non_http_urls(client, url):
    assert client.post("/api/analyze", json={"url": url}).status_code == 422


def test_analyze_with_injected_extractor(models_dir):
    seen = []

    def fake_extractor(url):  # test double: no network access
        seen.append(url)
        return HIGH

    with make_client(models_dir, extractor=fake_extractor) as c:
        body = c.post("/api/analyze", json={"url": "https://example.com", "mode": "best"}).json()
        specific = c.post("/api/analyze", json={"url": "https://example.com", "mode": "specific", "model": "SVM"}).json()
        compare = c.post("/api/analyze", json={"url": "https://example.com", "mode": "compare"})
    assert body["verdict"] == "phishing" and body["modelName"] == "Random Forest"
    assert 0 <= body["confidence"] <= 1
    assert specific["modelName"] == "SVM" and "confidence" not in specific
    assert compare.status_code == 422
    assert seen[0] == "https://example.com"


def test_analyze_extraction_failure_is_502(models_dir):
    def broken(url):
        raise ExtractionError()

    with make_client(models_dir, extractor=broken) as c:
        assert c.post("/api/analyze", json={"url": "https://example.com"}).status_code == 502


def test_cors_allows_only_configured_origin(client):
    ok = client.options("/api/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    bad = client.options("/api/health", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "access-control-allow-origin" not in bad.headers
