from __future__ import annotations

import json
import urllib.error
from io import BytesIO
from unittest.mock import patch

import pytest

from app.remote_query import call_v1_query, check_v1_ready


def test_call_v1_query_parses_response() -> None:
    payload = {
        "plan": {"intent": "unknown", "planner_source": "rules"},
        "execution": {"status": "success", "source": "system", "output": "ok"},
    }
    data = json.dumps(payload).encode()

    class _Resp:
        def read(self) -> bytes:
            return data

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *a: object) -> None:
            return None

    with patch("app.remote_query.urllib.request.urlopen", return_value=_Resp()):
        plan, ex = call_v1_query("http://127.0.0.1:9", "hi", use_llm=False, timeout_s=1.0)

    assert plan["intent"] == "unknown"
    assert ex["output"] == "ok"


def test_check_v1_ready_ok() -> None:
    data = json.dumps({"status": "ready", "duckdb": "/tmp/w.duckdb"}).encode()

    class _Resp:
        def read(self) -> bytes:
            return data

        def getcode(self) -> int:
            return 200

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *a: object) -> None:
            return None

    with patch("app.remote_query.urllib.request.urlopen", return_value=_Resp()):
        code, body = check_v1_ready("http://127.0.0.1:9", timeout_s=1.0)

    assert code == 200
    assert body["status"] == "ready"
    assert body["duckdb"] == "/tmp/w.duckdb"


def test_check_v1_ready_http_503() -> None:
    err = urllib.error.HTTPError(
        "http://x/ready",
        503,
        "Service Unavailable",
        {},
        BytesIO(b'{"detail":"parent missing"}'),
    )
    with patch("app.remote_query.urllib.request.urlopen", side_effect=err):
        code, body = check_v1_ready("http://127.0.0.1:9", timeout_s=1.0)

    assert code == 503
    assert body["detail"] == "parent missing"


def test_call_v1_query_fails_when_check_ready_and_503() -> None:
    err = urllib.error.HTTPError(
        "http://x/ready",
        503,
        "Service Unavailable",
        {},
        BytesIO(b'{"detail":"nope"}'),
    )
    with patch("app.remote_query.urllib.request.urlopen", side_effect=err):
        with pytest.raises(RuntimeError, match="readiness check failed"):
            call_v1_query("http://127.0.0.1:9", "q", use_llm=False, check_ready=True)


def test_call_v1_query_http_error() -> None:
    err = urllib.error.HTTPError(
        "http://x",
        401,
        "Unauthorized",
        {},
        BytesIO(b'{"detail":"nope"}'),
    )
    with patch("app.remote_query.urllib.request.urlopen", side_effect=err):
        with pytest.raises(RuntimeError, match="HTTP 401"):
            call_v1_query("http://127.0.0.1:9", "q", use_llm=False, timeout_s=1.0)
