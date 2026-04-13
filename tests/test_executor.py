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
