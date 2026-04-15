from __future__ import annotations

from app.llm_planner import parse_plan_json_safe


def test_parse_plan_json_safe_rejects_non_json() -> None:
    assert parse_plan_json_safe("not json") is None


def test_parse_plan_json_safe_rejects_non_object_payload() -> None:
    assert parse_plan_json_safe('["x"]') is None


def test_parse_plan_json_safe_rejects_invalid_intent_action() -> None:
    bad_intent = '{"intent":"nope","action":"query_ingestion_runs","message":"x","time_filter":null,"entity_filter":null}'
    assert parse_plan_json_safe(bad_intent) is None

    bad_action = '{"intent":"unknown","action":"do_stuff","message":"x","time_filter":null,"entity_filter":null}'
    assert parse_plan_json_safe(bad_action) is None


def test_parse_plan_json_safe_accepts_valid_payload() -> None:
    raw = (
        '{"intent":"pipeline_failure_lookup","action":"analyze_pipeline_failure","message":"x",'
        '"time_filter":{"label":"yesterday","start_time":"2026-04-14T00:00:00","end_time":"2026-04-15T00:00:00"},'
        '"entity_filter":{"config_path":null,"pipeline_name":"orders","dataset_name":null}}'
    )
    plan = parse_plan_json_safe(raw)
    assert plan is not None
    assert plan.planner_source == "llm"
    assert plan.intent == "pipeline_failure_lookup"
    assert plan.action == "analyze_pipeline_failure"
    assert plan.time_filter is not None
    assert plan.entity_filter is not None
    assert plan.entity_filter.pipeline_name == "orders"

