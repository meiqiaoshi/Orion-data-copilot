"""Optional shared-secret auth for the HTTP API (set ``ORION_API_KEY``)."""

from __future__ import annotations

import os
import secrets

from fastapi import Header, HTTPException


def configured_api_key() -> str | None:
    raw = os.environ.get("ORION_API_KEY", "")
    s = raw.strip()
    return s if s else None


def verify_api_key_if_configured(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    expected = configured_api_key()
    if expected is None:
        return
    provided: str | None = None
    if x_api_key is not None:
        provided = x_api_key.strip()
    elif authorization is not None and authorization.lower().startswith("bearer "):
        provided = authorization[7:].strip()
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
