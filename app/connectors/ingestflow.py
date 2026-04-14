from __future__ import annotations

from typing import Any
import duckdb

from app.schemas import EntityFilter, TimeFilter


def get_failed_ingestion_runs(
    db_path: str = "warehouse.duckdb",
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    base_query = """
        SELECT
            run_id,
            status,
            start_time,
            end_time,
            rows_loaded,
            config_path
        FROM ingestion_runs
        WHERE status = 'failed'
    """

    params: list[Any] = []

    if time_filter is not None:
        base_query += """
            AND start_time >= ?
            AND start_time < ?
        """
        params.extend([time_filter.start_time, time_filter.end_time])

    if entity_filter is not None and entity_filter.config_path is not None:
        base_query += """
            AND config_path ILIKE ?
        """
        params.append(f"%{entity_filter.config_path}%")

    if entity_filter is not None and entity_filter.pipeline_name is not None:
        base_query += """
            AND config_path ILIKE ?
        """
        params.append(f"%{entity_filter.pipeline_name}%")

    base_query += """
        ORDER BY start_time DESC
        LIMIT ?
    """
    params.append(limit)

    con = None
    try:
        con = duckdb.connect(db_path)
        result = con.execute(base_query, params)
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as exc:
        return [{"error": str(exc)}]
    finally:
        if con is not None:
            con.close()


def get_recent_ingestion_runs(
    db_path: str = "warehouse.duckdb",
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    base_query = """
        SELECT
            run_id,
            status,
            start_time,
            end_time,
            rows_loaded,
            config_path
        FROM ingestion_runs
        WHERE 1 = 1
    """

    params: list[Any] = []

    if time_filter is not None:
        base_query += """
            AND start_time >= ?
            AND start_time < ?
        """
        params.extend([time_filter.start_time, time_filter.end_time])

    if entity_filter is not None and entity_filter.config_path is not None:
        base_query += """
            AND config_path ILIKE ?
        """
        params.append(f"%{entity_filter.config_path}%")

    if entity_filter is not None and entity_filter.pipeline_name is not None:
        base_query += """
            AND config_path ILIKE ?
        """
        params.append(f"%{entity_filter.pipeline_name}%")

    base_query += """
        ORDER BY start_time DESC
        LIMIT ?
    """
    params.append(limit)

    con = None
    try:
        con = duckdb.connect(db_path)
        result = con.execute(base_query, params)
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as exc:
        return [{"error": str(exc)}]
    finally:
        if con is not None:
            con.close()