from __future__ import annotations

from typing import Any

from app.schemas import EntityFilter, TimeFilter

try:
    # Optional dependency (used only when available).
    from sentineldq.metadata.store import get_recent_alerts  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover
    get_recent_alerts = None  # type: ignore[assignment]


def get_recent_dq_alerts(
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    try:
        if get_recent_alerts is None:
            raise ModuleNotFoundError("No module named 'sentineldq'")

        rows = get_recent_alerts(limit=limit)

        results = [
            {
                "created_at": row[0],
                "severity": row[1],
                "rule_name": row[2],
                "table_name": row[3],
                "message": row[4],
            }
            for row in rows
        ]

        if time_filter is not None:
            results = [
                row
                for row in results
                if row["created_at"] >= time_filter.start_time.isoformat()
                and row["created_at"] < time_filter.end_time.isoformat()
            ]

        if entity_filter is not None and entity_filter.dataset_name is not None:
            needle = entity_filter.dataset_name.lower()
            results = [
                row
                for row in results
                if needle in str(row["table_name"]).lower()
            ]

        if entity_filter is not None and entity_filter.pipeline_name is not None:
            needle = entity_filter.pipeline_name.lower()
            results = [
                row
                for row in results
                if needle in str(row["table_name"]).lower()
                or needle in str(row["message"]).lower()
            ]

        return results

    except Exception as exc:
        return [{"error": str(exc)}]