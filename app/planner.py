from __future__ import annotations

from app.entity_parser import (
    parse_config_path,
    parse_dataset_name,
    parse_pipeline_name,
)
from app.llm_planner import plan_query_with_llm
from app.schemas import EntityFilter, PlanResult, TimeFilter, UserQuery
from app.time_parser import parse_time_window


def _plan_query_with_rules(query: UserQuery) -> PlanResult:
    text = query.raw_text.lower()
    parsed_window = parse_time_window(query.raw_text)

    time_filter = None
    if parsed_window is not None:
        time_filter = TimeFilter(
            label=parsed_window.label,
            start_time=parsed_window.start_time,
            end_time=parsed_window.end_time,
        )

    config_path = parse_config_path(query.raw_text)
    pipeline_name = parse_pipeline_name(query.raw_text)
    dataset_name = parse_dataset_name(query.raw_text)

    entity_filter = None
    if any(
        [
            config_path is not None,
            pipeline_name is not None,
            dataset_name is not None,
        ]
    ):
        entity_filter = EntityFilter(
            config_path=config_path,
            pipeline_name=pipeline_name,
            dataset_name=dataset_name,
        )

    if "fail" in text or "failed" in text or "failure" in text:
        if "why" in text or "root cause" in text or "cause" in text:
            return PlanResult(
                intent="pipeline_failure_lookup",
                action="analyze_pipeline_failure",
                message="This query looks like a request to analyze why an ingestion run failed.",
                time_filter=time_filter,
                entity_filter=entity_filter,
                planner_source="rules",
            )
        return PlanResult(
            intent="pipeline_failure_lookup",
            action="query_ingestion_runs",
            message="This query looks like a request to inspect failed ingestion runs.",
            time_filter=time_filter,
            entity_filter=entity_filter,
            planner_source="rules",
        )

    if "recent" in text or "latest" in text:
        if "run" in text or "runs" in text or "jobs" in text:
            return PlanResult(
                intent="pipeline_run_lookup",
                action="query_recent_ingestion_runs",
                message="This query looks like a request to inspect recent ingestion runs.",
                time_filter=time_filter,
                entity_filter=entity_filter,
                planner_source="rules",
            )

    if (
        "quality" in text
        or "unhealthy" in text
        or "dq" in text
        or "data quality" in text
        or "issues" in text
        or "alert" in text
        or "alerts" in text
    ):
        return PlanResult(
            intent="data_quality_lookup",
            action="query_sentineldq_issues",
            message="This query looks like a request to inspect data quality alerts.",
            time_filter=time_filter,
            entity_filter=entity_filter,
            planner_source="rules",
        )

    return PlanResult(
        intent="unknown",
        action="clarify_or_fallback",
        message="I could not confidently classify this query yet.",
        time_filter=time_filter,
        entity_filter=entity_filter,
        planner_source="rules",
    )


def plan_query(query: UserQuery, use_llm: bool = True) -> PlanResult:
    if use_llm:
        llm_plan = plan_query_with_llm(query)
        if llm_plan is not None:
            return llm_plan

    return _plan_query_with_rules(query)
