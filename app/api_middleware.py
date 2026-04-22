"""HTTP middleware for the FastAPI app."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


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
