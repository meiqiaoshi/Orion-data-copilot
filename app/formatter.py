from __future__ import annotations

from typing import Any

from app.schemas import EntityFilter, TimeFilter


def _build_filter_text(
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filters: list[str] = []

    if time_filter is not None:
        filters.append(f"{time_filter.label.replace('_', ' ')}")

    if entity_filter is not None:
        if entity_filter.config_path is not None:
            filters.append(f"config '{entity_filter.config_path}'")
        if entity_filter.dataset_name is not None:
            filters.append(f"dataset '{entity_filter.dataset_name}'")

    if not filters:
        return ""

    return " for " + ", ".join(filters)


# -----------------------------
# IngestFlow (failed runs)
# -----------------------------
def format_failed_ingestion_runs(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not rows:
        return f"I couldn't find any failed ingestion runs{filter_text}."

    count = len(rows)

    latest = rows[0]
    summary = (
        f"I found {count} failed ingestion run(s){filter_text}.\n\n"
        f"The most recent failure occurred at {latest.get('start_time')}."
    )

    details = []
    for i, row in enumerate(rows, 1):
        details.append(
            f"{i}. run {row.get('run_id')} "
            f"(rows_loaded={row.get('rows_loaded')}) "
            f"at {row.get('start_time')}"
        )

    return summary + "\n\nRecent failures:\n" + "\n".join(details)


# -----------------------------
# IngestFlow (recent runs)
# -----------------------------
def format_recent_ingestion_runs(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not rows:
        return f"I couldn't find any ingestion runs{filter_text}."

    count = len(rows)

    latest = rows[0]
    summary = (
        f"I found {count} recent ingestion run(s){filter_text}.\n\n"
        f"The latest run has status '{latest.get('status')}' "
        f"and started at {latest.get('start_time')}."
    )

    details = []
    for i, row in enumerate(rows, 1):
        details.append(
            f"{i}. {row.get('status')} – run {row.get('run_id')} "
            f"at {row.get('start_time')}"
        )

    return summary + "\n\nRecent runs:\n" + "\n".join(details)


# -----------------------------
# SentinelDQ (alerts)
# -----------------------------
def format_dq_alerts(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not rows:
        return f"I couldn't find any data quality issues{filter_text}."

    count = len(rows)

    # high severity first
    severity_rank = {"high": 3, "medium": 2, "low": 1}
    sorted_rows = sorted(
        rows,
        key=lambda r: severity_rank.get(str(r.get("severity")).lower(), 0),
        reverse=True,
    )

    top_issue = sorted_rows[0]

    summary = (
        f"I found {count} data quality alert(s){filter_text}.\n\n"
        f"The most critical issue is a {top_issue.get('severity')} severity "
        f"{top_issue.get('rule_name')} in dataset '{top_issue.get('table_name')}'."
    )

    details = []
    for i, row in enumerate(rows, 1):
        details.append(
            f"{i}. {row.get('table_name')} "
            f"({row.get('severity')}) – {row.get('rule_name')} "
            f"at {row.get('created_at')}"
        )

    return summary + "\n\nRecent alerts:\n" + "\n".join(details)