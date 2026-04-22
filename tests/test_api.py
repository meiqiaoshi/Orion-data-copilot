from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.api import app
from app.version import __version__


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root_lists_entrypoints(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "orion-data-copilot"
    assert body["version"] == __version__
    assert body["docs"] == "/docs"
    assert body["plan"] == "POST /v1/plan"


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_v1_version(client: TestClient) -> None:
    r = client.get("/v1/version")
    assert r.status_code == 200
    assert r.json() == {"version": __version__}


def test_openapi_docs_available(client: TestClient) -> None:
    r = client.get("/docs")
    assert r.status_code == 200


def test_query_rules_only(client: TestClient) -> None:
    r = client.post(
        "/v1/query",
        json={"query": "what is the weather", "use_llm": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert "plan" in body and "execution" in body
    assert body["plan"]["intent"] == "unknown"
    assert "status" in body["execution"]


def test_plan_rules_only_no_execution(client: TestClient) -> None:
    r = client.post(
        "/v1/plan",
        json={"query": "what is the weather", "use_llm": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"plan"}
    assert body["plan"]["intent"] == "unknown"


def test_query_rejects_whitespace_only(client: TestClient) -> None:
    r = client.post("/v1/query", json={"query": "   ", "use_llm": False})
    assert r.status_code == 422


def test_plan_rejects_whitespace_only(client: TestClient) -> None:
    r = client.post("/v1/plan", json={"query": "   ", "use_llm": False})
    assert r.status_code == 422


def test_v1_routes_require_api_key_when_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ORION_API_KEY", "test-secret-key")

    v = client.get("/v1/version")
    assert v.status_code == 401

    q = client.post(
        "/v1/query",
        json={"query": "what is the weather", "use_llm": False},
    )
    assert q.status_code == 401

    p = client.post(
        "/v1/plan",
        json={"query": "what is the weather", "use_llm": False},
    )
    assert p.status_code == 401

    v_ok = client.get("/v1/version", headers={"X-API-Key": "test-secret-key"})
    assert v_ok.status_code == 200

    q_ok = client.post(
        "/v1/query",
        json={"query": "what is the weather", "use_llm": False},
        headers={"Authorization": "Bearer test-secret-key"},
    )
    assert q_ok.status_code == 200

    p_ok = client.post(
        "/v1/plan",
        json={"query": "what is the weather", "use_llm": False},
        headers={"X-API-Key": "test-secret-key"},
    )
    assert p_ok.status_code == 200


def test_health_unauthenticated_when_api_key_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ORION_API_KEY", "secret")
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_wrong_api_key_returns_401(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ORION_API_KEY", "expected")
    r = client.get("/v1/version", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401
