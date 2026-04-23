"""Call the local HTTP API (`/v1/query`) — used by optional Streamlit remote mode."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def call_v1_query(
    base_url: str,
    query: str,
    use_llm: bool,
    *,
    timeout_s: float = 120.0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    POST to ``{base}/v1/query`` with ``{"query", "use_llm"}``.

    If ``ORION_API_KEY`` is set, sends it as ``X-API-Key`` (for servers that
    require ``ORION_API_KEY``).
    """
    root = base_url.strip().rstrip("/")
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
