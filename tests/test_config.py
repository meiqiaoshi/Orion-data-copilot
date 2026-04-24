from __future__ import annotations

import pytest

from app.config import (
    api_post_rate_limit_spec,
    cors_allow_origins,
    duckdb_runtime_ready,
    resolve_duckdb_path,
    resolve_openai_model,
)


def test_cors_allow_origins_default_wildcard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORION_CORS_ORIGINS", raising=False)
    assert cors_allow_origins() == ["*"]


def test_cors_allow_origins_explicit_star(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_CORS_ORIGINS", "*")
    assert cors_allow_origins() == ["*"]


def test_cors_allow_origins_comma_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ORION_CORS_ORIGINS",
        "https://a.example, http://localhost:3000 ,",
    )
    assert cors_allow_origins() == ["https://a.example", "http://localhost:3000"]


def test_cors_allow_origins_empty_parts_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_CORS_ORIGINS", "  ,  , ")
    assert cors_allow_origins() == ["*"]


def test_resolve_explicit_wins_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_DUCKDB_PATH", "/env/warehouse.duckdb")
    assert resolve_duckdb_path("/explicit.duckdb") == "/explicit.duckdb"


def test_resolve_env_when_no_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_DUCKDB_PATH", "/data/meta.duckdb")
    assert resolve_duckdb_path(None) == "/data/meta.duckdb"


def test_resolve_default_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORION_DUCKDB_PATH", raising=False)
    assert resolve_duckdb_path(None) == "warehouse.duckdb"


def test_resolve_explicit_empty_string_falls_through(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_DUCKDB_PATH", "/from/env.duckdb")
    assert resolve_duckdb_path("   ") == "/from/env.duckdb"


def test_resolve_openai_model_explicit_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_OPENAI_MODEL", "gpt-4o-mini")
    assert resolve_openai_model("gpt-4o") == "gpt-4o"


def test_resolve_openai_model_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_OPENAI_MODEL", "gpt-4o-mini")
    assert resolve_openai_model(None) == "gpt-4o-mini"


def test_resolve_openai_model_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORION_OPENAI_MODEL", raising=False)
    assert resolve_openai_model(None) == "gpt-5"


def test_api_post_rate_limit_spec_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORION_API_RATE_LIMIT_POST", raising=False)
    assert api_post_rate_limit_spec() == "60/minute"


def test_api_post_rate_limit_spec_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_API_RATE_LIMIT_POST", "30/second")
    assert api_post_rate_limit_spec() == "30/second"


def test_api_post_rate_limit_spec_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORION_API_RATE_LIMIT_POST", "off")
    assert api_post_rate_limit_spec() == "1000000/minute"


def test_duckdb_runtime_ready_creatable_in_empty_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ORION_DUCKDB_PATH", raising=False)
    ok, err = duckdb_runtime_ready(None)
    assert ok is True
    assert err == ""


def test_duckdb_runtime_ready_existing_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    db = tmp_path / "meta.duckdb"
    db.write_bytes(b"")
    monkeypatch.setenv("ORION_DUCKDB_PATH", str(db))
    ok, err = duckdb_runtime_ready(None)
    assert ok is True
    assert err == ""


def test_duckdb_runtime_ready_parent_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ORION_DUCKDB_PATH",
        "/this_path_should_not_exist_on_ci_zzzz/sub/db.duckdb",
    )
    ok, err = duckdb_runtime_ready(None)
    assert ok is False
    assert "parent" in err.lower() or "missing" in err.lower()


def test_duckdb_runtime_ready_path_is_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    d = tmp_path / "not_a_file"
    d.mkdir()
    monkeypatch.setenv("ORION_DUCKDB_PATH", str(d))
    ok, err = duckdb_runtime_ready(None)
    assert ok is False
    assert "regular file" in err.lower()
