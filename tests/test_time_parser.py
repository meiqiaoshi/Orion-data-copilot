from __future__ import annotations

from app.time_parser import parse_time_window


def test_parse_last_n_days_english() -> None:
    w = parse_time_window("failed jobs in last 7 days")
    assert w is not None
    assert w.label == "last_7_days"


def test_parse_yesterday_english() -> None:
    w = parse_time_window("pipeline failed yesterday")
    assert w is not None
    assert w.label == "yesterday"
