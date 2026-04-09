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


def execute_plan(plan: PlanResult) -> ExecutionResult:
    if plan.action == "query_ingestion_runs":
        data = get_failed_ingestion_runs(
            time_filter=plan.time_filter,
            entity_filter=plan.entity_filter,
        )

        if data and "error" in data[0]:
            return ExecutionResult(
                status="error",
                source="ingestflow",
                output=data[0]["error"],
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

        if data and "error" in data[0]:
            return ExecutionResult(
                status="error",
                source="ingestflow",
                output=data[0]["error"],
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

        if data and "error" in data[0]:
            return ExecutionResult(
                status="error",
                source="sentineldq",
                output=data[0]["error"],
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
        output="No executable handler is available for this query yet.",
    )