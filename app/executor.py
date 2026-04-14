from __future__ import annotations

from datetime import datetime, timedelta

from app.connectors.ingestflow import (
    get_failed_ingestion_runs,
    get_recent_ingestion_runs,
)
from app.connectors.sentineldq import get_recent_dq_alerts
from app.formatter import (
    format_dq_alerts,
    format_failed_ingestion_runs,
    format_root_cause_report,
    format_recent_ingestion_runs,
)
from app.schemas import ExecutionResult, PlanResult, TimeFilter


def _build_user_friendly_error(source: str, error_text: str) -> str:
    normalized = error_text.lower()

    if "no module named" in normalized and "sentineldq" in normalized:
        return (
            "I couldn't access SentinelDQ because the package is not available in "
            "the current environment. Please install SentinelDQ or make sure it is "
            "importable before running this query."
        )

    if "table with name ingestion_runs does not exist" in normalized:
        return (
            "I couldn't query the ingestion metadata store because the "
            "'ingestion_runs' table was not found. Please verify the DuckDB path "
            "and confirm the IngestFlow schema exists."
        )

    if "no such table: alerts" in normalized or "table alerts does not exist" in normalized:
        return (
            "I couldn't query SentinelDQ alerts because the 'alerts' table was not "
            "found. Please verify the SentinelDQ metadata database path and schema."
        )

    if "no such table" in normalized:
        return (
            f"I couldn't query the {source} metadata store because an expected table "
            "was not found. Please verify the database path and schema."
        )

    if "permission" in normalized or "access" in normalized:
        return (
            f"I couldn't access the {source} metadata store due to a permissions "
            "issue. Please verify file access and environment configuration."
        )

    if "unable to open database file" in normalized:
        return (
            f"I couldn't open the {source} metadata database. Please verify the "
            "configured database path and make sure the file exists."
        )

    return (
        f"I ran into an error while querying the {source} metadata store. "
        f"Details: {error_text}"
    )


def _is_error_result(data: list[dict]) -> bool:
    return bool(data) and isinstance(data[0], dict) and "error" in data[0]


def _parse_dt(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def _derive_time_filter_from_failure(failures: list[dict]) -> TimeFilter | None:
    if not failures:
        return None

    latest = failures[0]
    start = _parse_dt(latest.get("start_time"))
    if start is None:
        return None

    # Heuristic: DQ alerts tend to cluster around the failure; use a small window.
    window = timedelta(hours=6)
    return TimeFilter(
        label="around_failure",
        start_time=start - window,
        end_time=start + window,
    )


def _stem_from_config_path(config_path: str | None) -> str:
    if not config_path:
        return ""
    return config_path.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()


def _score_alert(
    alert: dict,
    *,
    entity_filter: object,
    failure_start: datetime | None,
    failure_config_path: str | None = None,
) -> tuple[int, list[str]]:
    # Score is additive; keep it simple and explainable.
    score = 0
    reasons: list[str] = []

    table = str(alert.get("table_name") or "").lower()
    message = str(alert.get("message") or "").lower()

    dataset = getattr(entity_filter, "dataset_name", None) if entity_filter is not None else None
    if isinstance(dataset, str) and dataset:
        needle = dataset.lower()
        if needle in table:
            score += 5
            reasons.append(f"dataset match: '{dataset}' in table_name")

    pipeline = getattr(entity_filter, "pipeline_name", None) if entity_filter is not None else None
    if isinstance(pipeline, str) and pipeline:
        needle = pipeline.lower()
        if needle in table or needle in message:
            score += 4
            reasons.append(f"pipeline match: '{pipeline}' in table_name/message")

    config_path = getattr(entity_filter, "config_path", None) if entity_filter is not None else None
    stem_from_query = _stem_from_config_path(config_path if isinstance(config_path, str) else None)
    if stem_from_query and (stem_from_query in table or stem_from_query in message):
        score += 2
        reasons.append(f"config keyword match: '{stem_from_query}'")

    stem_from_failure = _stem_from_config_path(failure_config_path)
    if stem_from_failure and (stem_from_failure in table or stem_from_failure in message):
        # Avoid double-counting when the query already specified the same config stem.
        if stem_from_query != stem_from_failure:
            score += 2
            reasons.append(f"failure run config stem match: '{stem_from_failure}'")

    created_at = _parse_dt(alert.get("created_at"))
    if created_at is not None and failure_start is not None:
        delta = abs((created_at - failure_start).total_seconds())
        if delta <= 3600:
            score += 3
            reasons.append("within 1h of failure")
        elif delta <= 6 * 3600:
            score += 1
            reasons.append("within 6h of failure")

    if score == 0:
        reasons.append("weak match (recency only)")

    return score, reasons


def execute_plan(plan: PlanResult) -> ExecutionResult:
    if plan.action == "analyze_pipeline_failure":
        failures = get_failed_ingestion_runs(
            time_filter=plan.time_filter,
            entity_filter=plan.entity_filter,
            limit=5,
        )

        if _is_error_result(failures):
            return ExecutionResult(
                status="error",
                source="ingestflow",
                output=_build_user_friendly_error("ingestflow", failures[0]["error"]),
            )

        if not failures:
            return ExecutionResult(
                status="success",
                source="system",
                output=format_root_cause_report(
                    failures=[],
                    dq_alerts=[],
                    time_filter=plan.time_filter,
                    entity_filter=plan.entity_filter,
                ),
            )

        derived_time_filter = plan.time_filter or _derive_time_filter_from_failure(failures)
        failure_start = _parse_dt(failures[0].get("start_time"))
        failure_cfg = failures[0].get("config_path")
        failure_config_path = failure_cfg if isinstance(failure_cfg, str) else None

        dq = get_recent_dq_alerts(
            time_filter=derived_time_filter,
            entity_filter=plan.entity_filter,
            limit=100,
        )

        dq_alerts: list[dict] = dq
        if _is_error_result(dq):
            dq_alerts = []
        else:
            scored: list[dict] = []
            for alert in dq_alerts:
                score, reasons = _score_alert(
                    alert,
                    entity_filter=plan.entity_filter,
                    failure_start=failure_start,
                    failure_config_path=failure_config_path,
                )
                enriched = dict(alert)
                enriched["_score"] = score
                enriched["_reasons"] = reasons
                scored.append(enriched)

            scored.sort(key=lambda a: int(a.get("_score", 0)), reverse=True)
            dq_alerts = scored[:10]

        return ExecutionResult(
            status="success",
            source="system",
            output=format_root_cause_report(
                failures=failures,
                dq_alerts=dq_alerts,
                time_filter=derived_time_filter,
                entity_filter=plan.entity_filter,
            ),
        )

    if plan.action == "query_ingestion_runs":
        data = get_failed_ingestion_runs(
            time_filter=plan.time_filter,
            entity_filter=plan.entity_filter,
        )

        if _is_error_result(data):
            return ExecutionResult(
                status="error",
                source="ingestflow",
                output=_build_user_friendly_error("ingestflow", data[0]["error"]),
            )

        return ExecutionResult(
            status="success",
            source="ingestflow",
            output=format_failed_ingestion_runs(
                rows=data,
                time_filter=plan.time_filter,
                entity_filter=plan.entity_filter,
            ),
        )

    if plan.action == "query_recent_ingestion_runs":
        data = get_recent_ingestion_runs(
            time_filter=plan.time_filter,
            entity_filter=plan.entity_filter,
        )

        if _is_error_result(data):
            return ExecutionResult(
                status="error",
                source="ingestflow",
                output=_build_user_friendly_error("ingestflow", data[0]["error"]),
            )

        return ExecutionResult(
            status="success",
            source="ingestflow",
            output=format_recent_ingestion_runs(
                rows=data,
                time_filter=plan.time_filter,
                entity_filter=plan.entity_filter,
            ),
        )

    if plan.action == "query_sentineldq_issues":
        data = get_recent_dq_alerts(
            time_filter=plan.time_filter,
            entity_filter=plan.entity_filter,
        )

        if _is_error_result(data):
            return ExecutionResult(
                status="error",
                source="sentineldq",
                output=_build_user_friendly_error("sentineldq", data[0]["error"]),
            )

        return ExecutionResult(
            status="success",
            source="sentineldq",
            output=format_dq_alerts(
                rows=data,
                time_filter=plan.time_filter,
                entity_filter=plan.entity_filter,
            ),
        )

    return ExecutionResult(
        status="not_implemented",
        source="system",
        output=(
            "I understood the query, but I don't have an execution path for it yet. "
            "Try asking about failed ingestion runs, recent ingestion runs, or data "
            "quality alerts."
        ),
    )