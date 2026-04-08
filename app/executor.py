from app.schemas import ExecutionResult, PlanResult


def execute_plan(plan: PlanResult) -> ExecutionResult:
    if plan.action == "query_ingestion_runs":
        return ExecutionResult(
            status="success",
            source="ingestflow",
            output=(
                "Mock result: found failed ingestion jobs from IngestFlow metadata store."
            ),
        )

    if plan.action == "query_sentineldq":
        return ExecutionResult(
            status="success",
            source="sentineldq",
            output=(
                "Mock result: found datasets with recent data quality issues."
            ),
        )

    return ExecutionResult(
        status="not_implemented",
        source="system",
        output="No executable handler is available for this query yet.",
    )