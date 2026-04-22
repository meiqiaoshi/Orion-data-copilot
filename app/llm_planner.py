from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from app.config import resolve_openai_model
from app.schemas import EntityFilter, PlanResult, TimeFilter, UserQuery

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore


def _plan_json_compact(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"))


def _build_system_prompt() -> str:
    examples = [
        (
            "User: Show failed ingestion jobs in the last 7 days for sample.yaml\nOutput:\n"
            + _plan_json_compact(
                {
                    "intent": "pipeline_failure_lookup",
                    "action": "query_ingestion_runs",
                    "message": "Inspect failed ingestion runs.",
                    "time_filter": {
                        "label": "last_7_days",
                        "start_time": "2026-04-08T00:00:00",
                        "end_time": "2026-04-15T00:00:00",
                    },
                    "entity_filter": {
                        "config_path": "sample.yaml",
                        "pipeline_name": None,
                        "dataset_name": None,
                    },
                }
            )
        ),
        (
            "User: Why did pipeline orders fail yesterday?\nOutput:\n"
            + _plan_json_compact(
                {
                    "intent": "pipeline_failure_lookup",
                    "action": "analyze_pipeline_failure",
                    "message": "Analyze likely causes by linking failures to DQ alerts.",
                    "time_filter": {
                        "label": "yesterday",
                        "start_time": "2026-04-14T00:00:00",
                        "end_time": "2026-04-15T00:00:00",
                    },
                    "entity_filter": {
                        "config_path": None,
                        "pipeline_name": "orders",
                        "dataset_name": None,
                    },
                }
            )
        ),
        (
            "User: Show recent ingestion runs for pipeline orders\nOutput:\n"
            + _plan_json_compact(
                {
                    "intent": "pipeline_run_lookup",
                    "action": "query_recent_ingestion_runs",
                    "message": "Inspect recent ingestion runs.",
                    "time_filter": None,
                    "entity_filter": {
                        "config_path": None,
                        "pipeline_name": "orders",
                        "dataset_name": None,
                    },
                }
            )
        ),
        (
            "User: Any data quality alerts for dataset raw_orders today?\nOutput:\n"
            + _plan_json_compact(
                {
                    "intent": "data_quality_lookup",
                    "action": "query_sentineldq_issues",
                    "message": "Inspect recent data quality alerts.",
                    "time_filter": {
                        "label": "today",
                        "start_time": "2026-04-15T00:00:00",
                        "end_time": "2026-04-15T12:00:00",
                    },
                    "entity_filter": {
                        "config_path": None,
                        "pipeline_name": None,
                        "dataset_name": "raw_orders",
                    },
                }
            )
        ),
    ]

    body = """
You are a query planning assistant for a data platform copilot.

Your job is to convert a user's natural language query into a structured JSON plan.

You must return valid JSON only.
Do not include markdown fences.
Do not include explanations.

Allowed intent values:
- pipeline_failure_lookup
- pipeline_run_lookup
- data_quality_lookup
- unknown

Allowed action values:
- query_ingestion_runs
- query_recent_ingestion_runs
- query_sentineldq_issues
- analyze_pipeline_failure
- clarify_or_fallback

Output schema:
{
  "intent": string,
  "action": string,
  "message": string,
  "time_filter": {
    "label": string,
    "start_time": string,
    "end_time": string
  } | null,
  "entity_filter": {
    "config_path": string | null,
    "pipeline_name": string | null,
    "dataset_name": string | null
  } | null
}

Guidelines:
- Use pipeline_failure_lookup + query_ingestion_runs for failed ingestion/job queries.
- Use pipeline_failure_lookup + analyze_pipeline_failure for "why did it fail" / root-cause style questions.
- Use pipeline_run_lookup + query_recent_ingestion_runs for recent/latest run queries.
- Use data_quality_lookup + query_sentineldq_issues for data quality, alert, unhealthy dataset queries.
- Use clarify_or_fallback when the user's request does not map clearly to a supported query.
- If the query mentions a config file like sample.yaml, put it in entity_filter.config_path.
- If the query mentions "pipeline X", put X in entity_filter.pipeline_name.
- If the query mentions "dataset X", put X in entity_filter.dataset_name.
- Only include a time_filter when the user explicitly references time.
- Use ISO 8601 datetime strings.

Examples (return JSON only):

""" + "\n\n".join(
        examples
    )

    return body.strip()


SYSTEM_PROMPT = _build_system_prompt()


_ALLOWED_INTENTS = {
    "pipeline_failure_lookup",
    "pipeline_run_lookup",
    "data_quality_lookup",
    "unknown",
}

_ALLOWED_ACTIONS = {
    "query_ingestion_runs",
    "query_recent_ingestion_runs",
    "query_sentineldq_issues",
    "analyze_pipeline_failure",
    "clarify_or_fallback",
}


def _build_time_filter_from_label(label: str) -> TimeFilter | None:
    now = datetime.now()

    if label.startswith("last_") and label.endswith("_days"):
        try:
            days = int(label.removeprefix("last_").removesuffix("_days"))
        except ValueError:
            return None

        return TimeFilter(
            label=label,
            start_time=now - timedelta(days=days),
            end_time=now,
        )

    if label == "yesterday":
        today_start = datetime(now.year, now.month, now.day)
        yesterday_start = today_start - timedelta(days=1)
        return TimeFilter(
            label="yesterday",
            start_time=yesterday_start,
            end_time=today_start,
        )

    if label == "today":
        today_start = datetime(now.year, now.month, now.day)
        return TimeFilter(
            label="today",
            start_time=today_start,
            end_time=now,
        )

    return None


def _parse_time_filter(payload: dict[str, Any] | None) -> TimeFilter | None:
    if payload is None:
        return None

    label = payload.get("label")
    start_time = payload.get("start_time")
    end_time = payload.get("end_time")

    if isinstance(label, str) and isinstance(start_time, str) and isinstance(end_time, str):
        try:
            return TimeFilter(
                label=label,
                start_time=datetime.fromisoformat(start_time),
                end_time=datetime.fromisoformat(end_time),
            )
        except ValueError:
            pass

    if isinstance(label, str):
        return _build_time_filter_from_label(label)

    return None


def _parse_entity_filter(payload: dict[str, Any] | None) -> EntityFilter | None:
    if payload is None:
        return None

    config_path = payload.get("config_path")
    pipeline_name = payload.get("pipeline_name")
    dataset_name = payload.get("dataset_name")

    if not any([config_path, pipeline_name, dataset_name]):
        return None

    return EntityFilter(
        config_path=config_path if isinstance(config_path, str) else None,
        pipeline_name=pipeline_name if isinstance(pipeline_name, str) else None,
        dataset_name=dataset_name if isinstance(dataset_name, str) else None,
    )


def parse_plan_json_safe(raw_json: str) -> PlanResult | None:
    """
    Parse and validate an LLM-produced JSON plan.

    Returns None when the payload is invalid, so the caller can safely fall back
    to rule-based planning.
    """
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    intent = payload.get("intent", "unknown")
    action = payload.get("action", "clarify_or_fallback")
    message = payload.get("message", "Generated by LLM planner.")

    if not isinstance(intent, str) or intent not in _ALLOWED_INTENTS:
        return None

    if not isinstance(action, str) or action not in _ALLOWED_ACTIONS:
        return None

    if not isinstance(message, str):
        return None

    time_filter = _parse_time_filter(payload.get("time_filter"))
    entity_filter = _parse_entity_filter(payload.get("entity_filter"))

    return PlanResult(
        intent=intent,  # type: ignore[arg-type]
        action=action,  # type: ignore[arg-type]
        message=message,
        time_filter=time_filter,
        entity_filter=entity_filter,
        planner_source="llm",
    )


def plan_query_with_llm(
    query: UserQuery,
    model: str | None = None,
) -> PlanResult | None:
    if OpenAI is None:
        return None

    try:
        client = OpenAI()
        model_name = resolve_openai_model(model)

        response = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query.raw_text},
            ],
            temperature=0,
        )

        raw_output = getattr(response, "output_text", None)
        if not raw_output or not isinstance(raw_output, str):
            return None

        return parse_plan_json_safe(raw_output)

    except Exception:
        return None