from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re


@dataclass(slots=True)
class TimeWindow:
    label: str
    start_time: datetime
    end_time: datetime


def parse_time_window(text: str) -> TimeWindow | None:
    normalized = text.strip().lower()
    now = datetime.now()

    last_n_days_match = re.search(r"last\s+(\d+)\s+days?", normalized)
    if last_n_days_match:
        days = int(last_n_days_match.group(1))
        return TimeWindow(
            label=f"last_{days}_days",
            start_time=now - timedelta(days=days),
            end_time=now,
        )

    if "yesterday" in normalized:
        today_start = datetime(now.year, now.month, now.day)
        yesterday_start = today_start - timedelta(days=1)
        return TimeWindow(
            label="yesterday",
            start_time=yesterday_start,
            end_time=today_start,
        )

    if "today" in normalized:
        today_start = datetime(now.year, now.month, now.day)
        return TimeWindow(
            label="today",
            start_time=today_start,
            end_time=now,
        )

    return None