from __future__ import annotations

from app.planner import plan_query
from app.schemas import UserQuery


def test_failed_jobs_maps_to_ingestion_runs() -> None:
    plan = plan_query(UserQuery("Show failed ingestion jobs"), use_llm=False)
    assert plan.intent == "pipeline_failure_lookup"
    assert plan.action == "query_ingestion_runs"
    assert plan.planner_source == "rules"


def test_why_failed_maps_to_root_cause_analysis() -> None:
    plan = plan_query(UserQuery("Why did pipeline X fail yesterday?"), use_llm=False)
    assert plan.intent == "pipeline_failure_lookup"
    assert plan.action == "analyze_pipeline_failure"


def test_recent_runs_maps_to_recent_ingestion() -> None:
    plan = plan_query(UserQuery("recent ingestion runs"), use_llm=False)
    assert plan.intent == "pipeline_run_lookup"
    assert plan.action == "query_recent_ingestion_runs"


def test_data_quality_maps_to_sentineldq() -> None:
    plan = plan_query(UserQuery("any data quality alerts?"), use_llm=False)
    assert plan.intent == "data_quality_lookup"
    assert plan.action == "query_sentineldq_issues"


def test_unknown_query_falls_back() -> None:
    plan = plan_query(UserQuery("what is the weather"), use_llm=False)
    assert plan.intent == "unknown"
    assert plan.action == "clarify_or_fallback"
