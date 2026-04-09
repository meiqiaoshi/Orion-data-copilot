from __future__ import annotations

from typing import Any
import duckdb

from app.schemas import TimeFilter


def get_failed_ingestion_runs(
    db_path: str = "warehouse.duckdb",
    time_filter: TimeFilter | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    base_query = """
        SELECT
            run_id,
            status,
            start_time,
            end_time,
            rows_loaded
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