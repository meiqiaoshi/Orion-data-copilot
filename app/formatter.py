from __future__ import annotations

from typing import Any

from app.schemas import TimeFilter


def format_failed_ingestion_runs(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
) -> str:
    if not rows:
        if time_filter is not None:
            return (
                f"No failed ingestion runs were found for time window "
                f"'{time_filter.label}'."
            )
        return "No failed ingestion runs were found."

    count = len(rows)

    if time_filter is not None:
        header = (
            f"Found {count} failed ingestion run(s) for time window "
            f"'{time_filter.label}'."
        )
    else:
        header = f"Found {count} failed ingestion run(s)."

    details: list[str] = []
    for index, row in enumerate(rows, start=1):
        run_id = row.get("run_id", "unknown")
        start_time = row.get("start_time", "unknown")
        end_time = row.get("end_time", "unknown")
        rows_loaded = row.get("rows_loaded", "unknown")

        details.append(
            f"{index}. run_id={run_id}, start_time={start_time}, "
            f"end_time={end_time}, rows_loaded={rows_loaded}"
        )

    return header + "\n" + "\n".join(details)