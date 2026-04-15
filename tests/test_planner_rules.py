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
    assert plan.entity_filter is not None
    assert plan.entity_filter.pipeline_name == "X"


def test_pipeline_name_extracted_for_failure_queries() -> None:
    plan = plan_query(UserQuery("Show failed jobs for pipeline orders"), use_llm=False)
    assert plan.entity_filter is not None
    assert plan.entity_filter.pipeline_name == "orders"


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


def test_chinese_why_failed_rca() -> None:
    plan = plan_query(UserQuery("为什么 pipeline p1 昨天失败"), use_llm=False)
    assert plan.action == "analyze_pipeline_failure"
    assert plan.entity_filter is not None
    assert plan.entity_filter.pipeline_name == "p1"


def test_chinese_recent_runs() -> None:
    plan = plan_query(UserQuery("最近 ingestion 运行"), use_llm=False)
    assert plan.intent == "pipeline_run_lookup"
    assert plan.action == "query_recent_ingestion_runs"


def test_chinese_data_quality() -> None:
    plan = plan_query(UserQuery("数据质量告警"), use_llm=False)
    assert plan.intent == "data_quality_lookup"
    assert plan.action == "query_sentineldq_issues"
