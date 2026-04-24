"""Runtime configuration helpers (environment-backed defaults)."""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_OPENAI_MODEL = "gpt-5"


def cors_allow_origins() -> list[str]:
    """
    Origins for FastAPI ``CORSMiddleware`` ``allow_origins``.

    Set ``ORION_CORS_ORIGINS`` to a comma-separated list (e.g. ``https://app.example.com,http://localhost:3000``).
    Use ``*`` or leave unset for permissive development (``["*"]``).
    """
    raw = os.environ.get("ORION_CORS_ORIGINS", "*").strip()
    if raw == "" or raw == "*":
        return ["*"]
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts if parts else ["*"]


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


def duckdb_runtime_ready(explicit: str | None = None) -> tuple[bool, str]:
    """
    Return ``(True, "")`` if the resolved DuckDB path looks usable from the process.

    Existing files require read access only (read-only volume mounts are OK). Missing
    files require a writable parent directory so DuckDB can create the database.
    """
    path_str = resolve_duckdb_path(explicit)
    p = Path(path_str).expanduser()
    try:
        p = p.resolve()
    except OSError as exc:
        return False, f"Invalid DuckDB path {path_str!r}: {exc}"

    parent = p.parent
    if not parent.is_dir():
        return False, f"DuckDB parent directory missing or not a directory: {parent}"

    if p.exists():
        if not p.is_file():
            return False, f"DuckDB path is not a regular file: {path_str!r}"
        if not os.access(p, os.R_OK):
            return False, f"DuckDB file is not readable: {path_str!r}"
        return True, ""

    if not os.access(parent, os.W_OK | os.X_OK):
        return False, f"Cannot create DuckDB file (parent not writable): {parent}"
    return True, ""
