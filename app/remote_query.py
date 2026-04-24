"""Call the local HTTP API (`/v1/query`) — used by optional Streamlit remote mode."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def check_v1_ready(base_url: str, *, timeout_s: float = 3.0) -> tuple[int, dict[str, Any]]:
    """
    GET ``{base}/ready`` — returns HTTP status code and parsed JSON body.

    If ``ORION_API_KEY`` is set, sends ``X-API-Key`` (optional; ``/ready`` does not
    require auth, but some proxies may expect the header).
    """
    root = base_url.strip().rstrip("/")
    url = f"{root}/ready"
    req = urllib.request.Request(url, method="GET")
    key = os.environ.get("ORION_API_KEY", "").strip()
    if key:
        req.add_header("X-API-Key", key)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = int(resp.getcode() or 200)
            body: Any = json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            body = {"detail": raw}
        if not isinstance(body, dict):
            body = {"detail": str(body)}
        return int(exc.code), body
    except OSError as exc:
        raise RuntimeError(f"Readiness request to {url} failed: {exc}") from exc

    if not isinstance(body, dict):
        return code, {"detail": str(body)}
    return code, body


def call_v1_query(
    base_url: str,
    query: str,
    use_llm: bool,
    *,
    timeout_s: float = 120.0,
    check_ready: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    POST to ``{base}/v1/query`` with ``{"query", "use_llm"}``.

    If ``ORION_API_KEY`` is set, sends it as ``X-API-Key`` (for servers that
    require ``ORION_API_KEY``).

    If ``check_ready`` is true, performs ``GET {base}/ready`` first and raises
    ``RuntimeError`` when the response is not HTTP 200.
    """
    root = base_url.strip().rstrip("/")
    if check_ready:
        rcode, rbody = check_v1_ready(root, timeout_s=min(10.0, float(timeout_s)))
        if rcode != 200:
            raise RuntimeError(
                f"API readiness check failed (HTTP {rcode}): {rbody!r}. "
                f"Open GET {root}/ready in a browser or fix ORION_DUCKDB_PATH on the server."
            )
    url = f"{root}/v1/query"
    body = json.dumps({"query": query, "use_llm": use_llm}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    key = os.environ.get("ORION_API_KEY", "").strip()
    if key:
        req.add_header("X-API-Key", key)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            payload: Any = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        msg = f"HTTP {exc.code} from {url}: {detail}"
        raise RuntimeError(msg) from exc
    except OSError as exc:
        raise RuntimeError(f"Request to {url} failed: {exc}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("API returned non-JSON object")
    plan = payload.get("plan")
    execution = payload.get("execution")
    if not isinstance(plan, dict) or not isinstance(execution, dict):
        raise RuntimeError("API response missing plan or execution objects")
    return plan, execution
