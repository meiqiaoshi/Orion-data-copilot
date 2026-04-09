from app.schemas import ExecutionResult, PlanResult
from app.connectors.ingestflow import get_failed_ingestion_runs


def execute_plan(plan: PlanResult) -> ExecutionResult:
    if plan.action == "query_ingestion_runs":
        data = get_failed_ingestion_runs()

        return ExecutionResult(
            status="success",
            source="ingestflow",
            output=str(data),
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