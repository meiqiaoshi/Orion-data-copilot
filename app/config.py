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


def api_post_rate_limit_spec() -> str:
    """
    slowapi limit for ``POST /v1/plan`` and ``POST /v1/query`` (e.g. ``60/minute``).

    Set ``ORION_API_RATE_LIMIT_POST`` to ``off``, ``0``, ``false``, or ``none`` for a
    very high effective cap (tests / private installs).
    """
    raw = os.environ.get("ORION_API_RATE_LIMIT_POST", "60/minute").strip()
    if raw.lower() in ("0", "off", "false", "none", ""):
        return "1000000/minute"
    return raw


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
