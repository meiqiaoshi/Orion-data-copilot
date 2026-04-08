from app.schemas import PlanResult, UserQuery


def plan_query(query: UserQuery) -> PlanResult:
    text = query.raw_text.lower()

    if "failed" in text or "failure" in text:
        return PlanResult(
            intent="pipeline_failure_lookup",
            action="query_ingestion_runs",
            message="This query looks like a request to inspect failed pipeline runs.",
        )

    if "quality" in text or "unhealthy" in text:
        return PlanResult(
            intent="data_quality_lookup",
            action="query_sentineldq",
            message="This query looks like a request to inspect data quality issues.",
        )

    return PlanResult(
        intent="unknown",
        action="clarify_or_fallback",
        message="I could not confidently classify this query yet.",
    )