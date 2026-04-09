from app.schemas import PlanResult, TimeFilter, UserQuery
from app.time_parser import parse_time_window


def plan_query(query: UserQuery) -> PlanResult:
    text = query.raw_text.lower()
    parsed_window = parse_time_window(query.raw_text)

    time_filter = None
    if parsed_window is not None:
        time_filter = TimeFilter(
            label=parsed_window.label,
            start_time=parsed_window.start_time,
            end_time=parsed_window.end_time,
        )

    if "failed" in text or "failure" in text:
        return PlanResult(
            intent="pipeline_failure_lookup",
            action="query_ingestion_runs",
            message="This query looks like a request to inspect failed pipeline runs.",
            time_filter=time_filter,
        )

    if "quality" in text or "unhealthy" in text:
        return PlanResult(
            intent="data_quality_lookup",
            action="query_sentineldq",
            message="This query looks like a request to inspect data quality issues.",
            time_filter=time_filter,
        )

    return PlanResult(
        intent="unknown",
        action="clarify_or_fallback",
        message="I could not confidently classify this query yet.",
        time_filter=time_filter,
    )