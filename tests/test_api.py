from __future__ import annotations

import logging
import uuid

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
    assert body["ready"] == "/ready"


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": __version__}
    rid = r.headers.get("x-request-id")
    assert rid
    uuid.UUID(rid)


def test_ready_ok_in_empty_tmp_dir(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ORION_DUCKDB_PATH", raising=False)
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["duckdb"].endswith("warehouse.duckdb")


def test_ready_503_when_parent_missing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(
        "ORION_DUCKDB_PATH",
        "/this_path_should_not_exist_on_ci_zzzz/sub/db.duckdb",
    )
    r = client.get("/ready")
    assert r.status_code == 503
    assert "detail" in r.json()


def test_ready_unauthenticated_when_api_key_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    monkeypatch.setenv("ORION_API_KEY", "secret")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ORION_DUCKDB_PATH", raising=False)
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_access_log_info_line(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="orion.api.access"):
        r = client.get("/health")
    assert r.status_code == 200
    messages = " ".join(caplog.messages)
    assert "GET" in messages
    assert "/health" in messages
    assert "200" in messages
    assert "ms rid=" in messages


def test_request_id_echoed_when_client_sends_header(client: TestClient) -> None:
    custom = "trace-abc-123"
    r = client.get("/health", headers={"X-Request-ID": custom})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == custom


def test_v1_version(client: TestClient) -> None:
    r = client.get("/v1/version")
    assert r.status_code == 200
    assert r.json() == {"version": __version__}


def test_openapi_docs_available(client: TestClient) -> None:
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_json_documents_optional_api_key_schemes(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemes = r.json()["components"]["securitySchemes"]
    assert schemes["ApiKeyHeader"]["type"] == "apiKey"
    assert schemes["ApiKeyHeader"]["name"] == "X-API-Key"
    assert schemes["BearerAuth"]["scheme"] == "bearer"
    desc = r.json()["info"]["description"]
    assert "Authentication" in desc
    assert "Rate limiting" in desc
    assert "429" in desc
    assert "Readiness" in desc


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
    assert r.json() == {"status": "ok", "version": __version__}


def test_wrong_api_key_returns_401(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ORION_API_KEY", "expected")
    r = client.get("/v1/version", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401
