from __future__ import annotations

from unittest.mock import patch

from app.executor import execute_plan
from app.schemas import ActionType, PlanResult


def _plan(action: ActionType) -> PlanResult:
    return PlanResult(
        intent="pipeline_failure_lookup",
        action=action,
        message="test",
    )


@patch("app.executor.get_failed_ingestion_runs")
def test_query_ingestion_runs_success(mock_get: object) -> None:
    mock_get.return_value = []

    result = execute_plan(_plan("query_ingestion_runs"))
    assert result.status == "success"
    assert result.source == "ingestflow"
    assert "failed ingestion runs" in result.output.lower()


@patch("app.executor.get_failed_ingestion_runs")
def test_query_ingestion_runs_connector_error(mock_get: object) -> None:
    mock_get.return_value = [{"error": "unable to open database file"}]

    result = execute_plan(_plan("query_ingestion_runs"))
    assert result.status == "error"
    assert result.source == "ingestflow"
    assert "couldn't open" in result.output.lower()


@patch("app.executor.get_recent_ingestion_runs")
def test_query_recent_ingestion_runs_success(mock_get: object) -> None:
    mock_get.return_value = [
        {
            "run_id": "r1",
            "status": "success",
            "start_time": None,
            "end_time": None,
            "rows_loaded": 1,
            "config_path": "c.yaml",
        }
    ]

    result = execute_plan(_plan("query_recent_ingestion_runs"))
    assert result.status == "success"
    assert result.source == "ingestflow"
    assert "r1" in result.output


@patch("app.executor.get_recent_dq_alerts")
def test_query_sentineldq_missing_package_error(mock_get: object) -> None:
    mock_get.return_value = [{"error": "No module named 'sentineldq'"}]

    result = execute_plan(_plan("query_sentineldq_issues"))
    assert result.status == "error"
    assert result.source == "sentineldq"
    assert "package is not available" in result.output.lower()


def test_clarify_or_fallback_not_implemented() -> None:
    result = execute_plan(_plan("clarify_or_fallback"))
    assert result.status == "not_implemented"
    assert result.source == "system"
    assert "don't have an execution path" in result.output


@patch("app.executor.get_failed_ingestion_runs")
@patch("app.executor.get_recent_dq_alerts")
def test_analyze_pipeline_failure_links_failure_and_dq(mock_dq: object, mock_failures: object) -> None:
    mock_failures.return_value = [
        {
            "run_id": "r2",
            "status": "failed",
            "start_time": "2026-04-14T00:00:00",
            "end_time": None,
            "rows_loaded": 0,
            "config_path": "sample.yaml",
        }
    ]
    mock_dq.return_value = [
        {
            "created_at": "2026-04-14T00:05:00",
            "severity": "high",
            "rule_name": "row_count_drop",
            "table_name": "raw_orders",
            "message": "Row count dropped",
        }
    ]

    result = execute_plan(_plan("analyze_pipeline_failure"))
    assert result.status == "success"
    assert result.source == "system"
    out = result.output.lower()
    assert "root-cause analysis" in out
    assert "latest failed run" in out
    assert "related data quality alerts" in out
