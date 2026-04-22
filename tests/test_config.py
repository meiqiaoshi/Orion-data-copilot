from __future__ import annotations

import pytest

from app.config import resolve_duckdb_path


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
