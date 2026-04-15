from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class TimeWindow:
    label: str
    start_time: datetime
    end_time: datetime


_CN_DIGIT: dict[str, int] = {
    "零": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "两": 2,
    "俩": 2,
}


def parse_cn_or_arabic_days(token: str) -> int | None:
    """
    Parse day counts like '7', '三', '二十五', '二十', '十一'.
    Returns None if the token is not a supported 1–365 day count.
    """
    token = token.strip()
    if not token:
        return None

    if token.isdigit():
        n = int(token)
        return n if 1 <= n <= 365 else None

    if token == "十":
        return 10

    if len(token) == 1:
        v = _CN_DIGIT.get(token)
        return v if v is not None and 1 <= v <= 365 else None

    if len(token) == 2:
        if token[0] == "十" and token[1] in _CN_DIGIT:
            return 10 + _CN_DIGIT[token[1]]
        if token[1] == "十" and token[0] in _CN_DIGIT:
            return _CN_DIGIT[token[0]] * 10

    if len(token) == 3 and token[1] == "十" and token[0] in _CN_DIGIT and token[2] in _CN_DIGIT:
        return _CN_DIGIT[token[0]] * 10 + _CN_DIGIT[token[2]]

    return None


def parse_time_window(text: str) -> TimeWindow | None:
    normalized = text.strip().lower()
    now = datetime.now()

    last_cn = re.search(
        r"(?:最近|过去)\s*([0-9一二三四五六七八九十两]+)\s*天",
        text,
    )
    if last_cn:
        days = parse_cn_or_arabic_days(last_cn.group(1))
        if days is not None:
            return TimeWindow(
                label=f"last_{days}_days",
                start_time=now - timedelta(days=days),
                end_time=now,
            )

    last_n_days_match = re.search(r"last\s+(\d+)\s+days?", normalized)
    if last_n_days_match:
        days = int(last_n_days_match.group(1))
        return TimeWindow(
            label=f"last_{days}_days",
            start_time=now - timedelta(days=days),
            end_time=now,
        )

    if "昨天" in text or "yesterday" in normalized:
        today_start = datetime(now.year, now.month, now.day)
        yesterday_start = today_start - timedelta(days=1)
        return TimeWindow(
            label="yesterday",
            start_time=yesterday_start,
            end_time=today_start,
        )

    if "今天" in text or "today" in normalized:
        today_start = datetime(now.year, now.month, now.day)
        return TimeWindow(
            label="today",
            start_time=today_start,
            end_time=now,
        )

    return None