"""Runtime configuration helpers (environment-backed defaults)."""

from __future__ import annotations

import os


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
