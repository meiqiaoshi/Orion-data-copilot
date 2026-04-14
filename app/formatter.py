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


def format_root_cause_report(
    failures: list[dict[str, Any]],
    dq_alerts: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not failures:
        return f"I couldn't find any failed ingestion runs{filter_text} to analyze."

    latest = failures[0]
    lines: list[str] = []
    lines.append(f"Root-cause analysis{filter_text}")
    lines.append("")
    lines.append("Failure signal:")
    lines.append(
        f"- latest failed run: {latest.get('run_id')} at {latest.get('start_time')} "
        f"(rows_loaded={latest.get('rows_loaded')})"
    )

    if dq_alerts and not (isinstance(dq_alerts[0], dict) and "error" in dq_alerts[0]):
        lines.append("")
        lines.append("Related data quality alerts (ranked heuristic match):")
        for i, alert in enumerate(dq_alerts[:10], 1):
            score = alert.get("_score")
            reasons = alert.get("_reasons") or []
            reason_text = ""
            if isinstance(reasons, list) and reasons:
                reason_text = " (" + "; ".join(str(r) for r in reasons[:3]) + ")"
            lines.append(
                f"{i}. score={score} [{alert.get('severity')}] {alert.get('rule_name')} on "
                f"{alert.get('table_name')} at {alert.get('created_at')}: {alert.get('message')}{reason_text}"
            )
    else:
        lines.append("")
        lines.append("Related data quality alerts: none found (or unavailable).")

    lines.append("")
    lines.append(
        "Next steps: validate whether the alerting tables/datasets overlap with the failed pipeline's outputs, "
        "and inspect logs around the failure time window."
    )

    return "\n".join(lines)


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