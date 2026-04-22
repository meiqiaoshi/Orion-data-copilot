"""Runtime configuration helpers (environment-backed defaults)."""

from __future__ import annotations

import os

_DEFAULT_OPENAI_MODEL = "gpt-5"


def resolve_openai_model(explicit: str | None) -> str:
    """Return OpenAI model name: explicit arg wins, then ``ORION_OPENAI_MODEL``, else default."""
    if explicit is not None:
        stripped = explicit.strip()
        if stripped:
            return stripped
    env = os.environ.get("ORION_OPENAI_MODEL", "").strip()
    if env:
        return env
    return _DEFAULT_OPENAI_MODEL


def resolve_duckdb_path(explicit: str | None) -> str:
    """Return DuckDB file path: explicit arg wins, then ``ORION_DUCKDB_PATH``, else ``warehouse.duckdb``."""
    if explicit is not None:
        stripped = explicit.strip()
        if stripped:
            return stripped
    env = os.environ.get("ORION_DUCKDB_PATH", "").strip()
    if env:
        return env
    return "warehouse.duckdb"
