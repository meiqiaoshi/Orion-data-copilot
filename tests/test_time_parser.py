from __future__ import annotations

from app.time_parser import parse_cn_or_arabic_days, parse_time_window


def test_parse_last_n_days_chinese() -> None:
    w = parse_time_window("最近7天失败任务")
    assert w is not None
    assert w.label == "last_7_days"


def test_parse_last_n_days_chinese_numerals() -> None:
    w = parse_time_window("最近三天失败任务")
    assert w is not None
    assert w.label == "last_3_days"


def test_parse_last_n_days_chinese_compound() -> None:
    w = parse_time_window("过去二十五天告警")
    assert w is not None
    assert w.label == "last_25_days"


def test_parse_cn_or_arabic_days() -> None:
    assert parse_cn_or_arabic_days("十一") == 11
    assert parse_cn_or_arabic_days("二十") == 20
    assert parse_cn_or_arabic_days("两") == 2


def test_parse_yesterday_chinese() -> None:
    w = parse_time_window("昨天 pipeline 失败")
    assert w is not None
    assert w.label == "yesterday"
