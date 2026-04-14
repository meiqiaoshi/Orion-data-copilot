from __future__ import annotations

from datetime import datetime

from app.formatter import format_root_cause_report
from app.schemas import TimeFilter


def test_root_cause_report_includes_config_path_and_dq_window() -> None:
    tf = TimeFilter(
        label="around_failure",
        start_time=datetime(2026, 4, 14, 0, 0, 0),
        end_time=datetime(2026, 4, 14, 12, 0, 0),
    )
    out = format_root_cause_report(
        failures=[
            {
                "run_id": "r1",
                "start_time": "2026-04-14T06:00:00",
                "rows_loaded": 0,
                "config_path": "configs/sample.yaml",
            }
        ],
        dq_alerts=[],
        time_filter=tf,
    )
    assert "config_path: configs/sample.yaml" in out
    assert "DQ alert lookup window:" in out
    assert "around_failure" in out
