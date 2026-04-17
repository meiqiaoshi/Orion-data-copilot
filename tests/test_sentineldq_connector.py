from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from app.connectors.sentineldq import get_recent_dq_alerts
from app.schemas import EntityFilter, TimeFilter


def _row(
    created_at: str,
    *,
    table: str = "raw_orders",
    message: str = "ok",
) -> tuple[str, str, str, str, str]:
    return (
        created_at,
        "high",
        "rule_x",
        table,
        message,
    )


@patch("app.connectors.sentineldq.get_recent_alerts")
def test_maps_rows_to_dicts(mock_alerts: object) -> None:
    mock_alerts.return_value = [_row("2026-04-16T12:00:00")]

    out = get_recent_dq_alerts(limit=5)
    assert len(out) == 1
    assert out[0]["severity"] == "high"
    assert out[0]["rule_name"] == "rule_x"
    assert out[0]["table_name"] == "raw_orders"
    assert out[0]["message"] == "ok"


@patch("app.connectors.sentineldq.get_recent_alerts")
def test_time_filter_keeps_rows_in_window(mock_alerts: object) -> None:
    mock_alerts.return_value = [
        _row("2026-04-16T08:00:00"),
        _row("2026-04-16T12:00:00"),
        _row("2026-04-16T18:00:00"),
    ]
    tf = TimeFilter(
        label="w",
        start_time=datetime.fromisoformat("2026-04-16T10:00:00"),
        end_time=datetime.fromisoformat("2026-04-16T14:00:00"),
    )

    out = get_recent_dq_alerts(time_filter=tf, limit=10)
    assert len(out) == 1
    assert out[0]["created_at"] == "2026-04-16T12:00:00"


@patch("app.connectors.sentineldq.get_recent_alerts")
def test_dataset_filter_matches_table_name(mock_alerts: object) -> None:
    mock_alerts.return_value = [
        _row("2026-04-16T12:00:00", table="staging_other"),
        _row("2026-04-16T12:00:00", table="raw_orders_v2"),
    ]
    ef = EntityFilter(dataset_name="raw_orders")

    out = get_recent_dq_alerts(entity_filter=ef, limit=10)
    assert len(out) == 1
    assert out[0]["table_name"] == "raw_orders_v2"


@patch("app.connectors.sentineldq.get_recent_alerts")
def test_pipeline_filter_matches_table_or_message(mock_alerts: object) -> None:
    mock_alerts.return_value = [
        _row("2026-04-16T12:00:00", table="t1", message="no match"),
        _row("2026-04-16T12:00:00", table="t2", message="pipeline orders failed"),
    ]
    ef = EntityFilter(pipeline_name="orders")

    out = get_recent_dq_alerts(entity_filter=ef, limit=10)
    assert len(out) == 1
    assert "orders" in out[0]["message"]


@patch("app.connectors.sentineldq.get_recent_alerts")
def test_exception_returns_error_payload(mock_alerts: object) -> None:
    mock_alerts.side_effect = RuntimeError("boom")

    out = get_recent_dq_alerts(limit=3)
    assert out == [{"error": "boom"}]
