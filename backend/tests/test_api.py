"""Contract tests. They run against the REAL model files and results_summary.csv.

Run from backend/:   pip install pytest httpx   then   pytest
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

IDS = ["xgboost", "random_forest", "logistic_regression"]


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:  # runs startup (loads models)
        yield c


def assert_error(r, status, code):
    assert r.status_code == status
    body = r.json()
    assert set(body) == {"error"} and body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "models": dict.fromkeys(IDS, True)}


def test_evaluation(client):
    r = client.get("/api/v1/evaluation")
    assert r.status_code == 200
    body = r.json()
    assert [m["model"] for m in body["models"]] == IDS
    for m in body["models"]:
        assert set(m["metrics"]) == {"accuracy", "precision", "recall", "f1", "roc_auc"}
        for k in ("accuracy", "precision", "recall", "f1"):
            assert 0 <= m["metrics"][k] <= 1
        assert m["metrics"]["roc_auc"] is None  # not in results_summary.csv
        assert m["confusion_matrix"] is None
    assert body["evaluation_samples"] is None


def test_predict_and_compare_agree(client):
    url = "https://example.com"
    p = client.post("/api/v1/predict", json={"url": url})
    c = client.post("/api/v1/compare", json={"url": url})
    assert p.status_code == c.status_code == 200
    p, c = p.json(), c.json()
    assert p["model"] == "xgboost" and p["url"] == c["url"] == url
    assert p["label"] in ("phishing", "legitimate")
    assert 0 <= p["phishing_probability"] <= 1
    assert [x["model"] for x in c["predictions"]] == IDS
    xgb = c["predictions"][0]
    assert (xgb["label"], xgb["phishing_probability"]) == (p["label"], p["phishing_probability"])
    for x in c["predictions"]:  # label must agree with probability at 0.5
        assert (x["label"] == "phishing") == (x["phishing_probability"] >= 0.5)


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"url": ""},
        {"url": "   "},
        {"url": 123},
        {"url": "ftp://example.com"},
        {"url": "example.com"},
        {"url": "http://"},
        {"url": "http://[bad"},
        {"url": "https://exa\nmple.com"},
        {"url": "https://example.com/" + "a" * 2048},
    ],
)
@pytest.mark.parametrize("path", ["/api/v1/predict", "/api/v1/compare"])
def test_invalid_url(client, path, body):
    assert_error(client.post(path, json=body), 422, "invalid_url")


def test_non_json_body(client):
    r = client.post("/api/v1/predict", content="nope", headers={"Content-Type": "application/json"})
    assert_error(r, 422, "invalid_url")


def test_cors(client):
    r = client.options(
        "/api/v1/predict",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_models_not_ready(client, monkeypatch):
    from app import model_service

    monkeypatch.setattr(model_service, "_models", {})
    assert client.get("/health").json()["status"] == "degraded"
    assert client.get("/health").status_code == 200
    assert_error(client.post("/api/v1/predict", json={"url": "https://example.com"}), 503, "models_not_ready")
    assert_error(client.post("/api/v1/compare", json={"url": "https://example.com"}), 503, "models_not_ready")
