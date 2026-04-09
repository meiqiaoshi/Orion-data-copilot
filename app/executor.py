from app.connectors.ingestflow import get_failed_ingestion_runs
from app.formatter import format_failed_ingestion_runs
from app.schemas import ExecutionResult, PlanResult


def execute_plan(plan: PlanResult) -> ExecutionResult:
    if plan.action == "query_ingestion_runs":
        data = get_failed_ingestion_runs(time_filter=plan.time_filter)

        if data and "error" in data[0]:
            return ExecutionResult(
                status="error",
                source="ingestflow",
                output=data[0]["error"],
            )

        formatted_output = format_failed_ingestion_runs(
            rows=data,
            time_filter=plan.time_filter,
        )

        return ExecutionResult(
            status="success",
            source="ingestflow",
            output=formatted_output,
        )

    if plan.action == "query_sentineldq":
        return ExecutionResult(
            status="not_implemented",
            source="sentineldq",
            output="SentinelDQ integration not implemented yet.",
        )

    return ExecutionResult(
        status="not_implemented",
        source="system",
        output="No executable handler is available for this query yet.",
    )