from __future__ import annotations

from typing import Any

from app.schemas import EntityFilter, TimeFilter


def _build_filter_text(
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filters: list[str] = []

    if time_filter is not None:
        filters.append(f"time window '{time_filter.label}'")

    if entity_filter is not None:
        if entity_filter.config_path is not None:
            filters.append(f"config path matching '{entity_filter.config_path}'")
        if entity_filter.pipeline_name is not None:
            filters.append(f"pipeline name '{entity_filter.pipeline_name}'")
        if entity_filter.dataset_name is not None:
            filters.append(f"dataset name '{entity_filter.dataset_name}'")

    if not filters:
        return ""

    return " for " + ", ".join(filters)


def format_failed_ingestion_runs(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not rows:
        return f"No failed ingestion runs were found{filter_text}."

    header = f"Found {len(rows)} failed ingestion run(s){filter_text}."

    details: list[str] = []
    for index, row in enumerate(rows, start=1):
        run_id = row.get("run_id", "unknown")
        start_time = row.get("start_time", "unknown")
        end_time = row.get("end_time", "unknown")
        rows_loaded = row.get("rows_loaded", "unknown")
        config_path = row.get("config_path", "unknown")

        details.append(
            f"{index}. run_id={run_id}, status=failed, start_time={start_time}, "
            f"end_time={end_time}, rows_loaded={rows_loaded}, config_path={config_path}"
        )

    return header + "\n" + "\n".join(details)


def format_recent_ingestion_runs(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not rows:
        return f"No ingestion runs were found{filter_text}."

    header = f"Found {len(rows)} recent ingestion run(s){filter_text}."

    details: list[str] = []
    for index, row in enumerate(rows, start=1):
        run_id = row.get("run_id", "unknown")
        status = row.get("status", "unknown")
        start_time = row.get("start_time", "unknown")
        end_time = row.get("end_time", "unknown")
        rows_loaded = row.get("rows_loaded", "unknown")
        config_path = row.get("config_path", "unknown")

        details.append(
            f"{index}. run_id={run_id}, status={status}, start_time={start_time}, "
            f"end_time={end_time}, rows_loaded={rows_loaded}, config_path={config_path}"
        )

    return header + "\n" + "\n".join(details)


def format_dq_alerts(
    rows: list[dict[str, Any]],
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
) -> str:
    filter_text = _build_filter_text(time_filter, entity_filter)

    if not rows:
        return f"No data quality alerts were found{filter_text}."

    header = f"Found {len(rows)} data quality alert(s){filter_text}."

    details: list[str] = []
    for index, row in enumerate(rows, start=1):
        created_at = row.get("created_at", "unknown")
        severity = row.get("severity", "unknown")
        rule_name = row.get("rule_name", "unknown")
        table_name = row.get("table_name", "unknown")
        message = row.get("message", "unknown")

        details.append(
            f"{index}. table_name={table_name}, severity={severity}, "
            f"rule_name={rule_name}, created_at={created_at}, message={message}"
        )

    return header + "\n" + "\n".join(details)