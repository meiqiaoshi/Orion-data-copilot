"""HTTP middleware for the FastAPI app."""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
ACCESS_LOG = logging.getLogger("orion.api.access")


def _access_log_enabled() -> bool:
    raw = os.environ.get("ORION_API_ACCESS_LOG", "1").strip().lower()
    return raw not in ("0", "false", "no", "off", "")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Emit one ``INFO`` line per request (method, path, status, duration, request id)."""

    def __init__(self, app: object, *, enabled: bool | None = None) -> None:
        super().__init__(app)
        if enabled is not None:
            self._enabled = enabled
        else:
            self._enabled = _access_log_enabled()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not self._enabled:
            return await call_next(request)
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:  # pragma: no cover - exercised when handlers raise
            elapsed = (time.perf_counter() - start) * 1000.0
            ACCESS_LOG.exception(
                "%s %s error after %.1fms",
                request.method,
                request.url.path,
                elapsed,
            )
            raise
        elapsed = (time.perf_counter() - start) * 1000.0
        rid = response.headers.get(REQUEST_ID_HEADER, "-")
        ACCESS_LOG.info(
            "%s %s %s %.1fms rid=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            rid,
        )
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach ``X-Request-ID`` to every response; reuse inbound header when non-empty."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        raw = request.headers.get(REQUEST_ID_HEADER)
        if raw is not None and raw.strip():
            request_id = raw.strip()
        else:
            request_id = str(uuid4())
        response: Response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
