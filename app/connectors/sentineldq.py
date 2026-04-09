from __future__ import annotations

from typing import Any
import duckdb

from app.schemas import EntityFilter, TimeFilter


def get_unhealthy_datasets(
    db_path: str = "warehouse.duckdb",
    time_filter: TimeFilter | None = None,
    entity_filter: EntityFilter | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    base_query = """
        SELECT
            dataset_name,
            status,
            run_time,
            check_name,
            severity
        FROM dq_runs
        WHERE status IN ('failed', 'warn', 'warning', 'unhealthy')
    """

    params: list[Any] = []

    if time_filter is not None:
        base_query += """
            AND run_time >= ?
            AND run_time < ?
        """
        params.extend([time_filter.start_time, time_filter.end_time])

    if entity_filter is not None and entity_filter.dataset_name is not None:
        base_query += """
            AND dataset_name ILIKE ?
        """
        params.append(f"%{entity_filter.dataset_name}%")

    base_query += """
        ORDER BY run_time DESC
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