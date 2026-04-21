from __future__ import annotations

from datetime import datetime, timezone

from app.json_serialization import json_safe
from app.schemas import EntityFilter, PlanResult, TimeFilter


def test_json_safe_datetime_isoformat() -> None:
    dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    assert json_safe({"t": dt}) == {"t": dt.isoformat()}


def test_plan_result_round_trip_dict_keys() -> None:
    from app.json_serialization import plan_result_to_dict

    plan = PlanResult(
        intent="unknown",
        action="clarify_or_fallback",
        message="test",
        time_filter=TimeFilter(
            label="7d",
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 8, tzinfo=timezone.utc),
        ),
        entity_filter=EntityFilter(pipeline_name="orders"),
        planner_source="rules",
    )
    d = plan_result_to_dict(plan)
    assert d["intent"] == "unknown"
    assert isinstance(d["time_filter"]["start_time"], str)
