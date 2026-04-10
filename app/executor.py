from __future__ import annotations

from app.connectors.ingestflow import (
    get_failed_ingestion_runs,
    get_recent_ingestion_runs,
)
from app.connectors.sentineldq import get_recent_dq_alerts
from app.formatter import (
    format_dq_alerts,
    format_failed_ingestion_runs,
    format_recent_ingestion_runs,
)
from app.schemas import ExecutionResult, PlanResult


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


def execute_plan(plan: PlanResult) -> ExecutionResult:
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