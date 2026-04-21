"""JSON-friendly dicts for plans and execution results (API, Streamlit, etc.)."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from app.schemas import ExecutionResult, PlanResult


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def plan_result_to_dict(plan: PlanResult) -> dict[str, Any]:
    return json_safe(asdict(plan))


def execution_result_to_dict(result: ExecutionResult) -> dict[str, Any]:
    return json_safe(asdict(result))
