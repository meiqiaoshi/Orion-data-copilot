from __future__ import annotations

from app.time_parser import parse_time_window


def test_parse_last_n_days_chinese() -> None:
    w = parse_time_window("最近7天失败任务")
    assert w is not None
    assert w.label == "last_7_days"


def test_parse_yesterday_chinese() -> None:
    w = parse_time_window("昨天 pipeline 失败")
    assert w is not None
    assert w.label == "yesterday"
