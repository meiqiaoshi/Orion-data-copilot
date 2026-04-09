import duckdb
from typing import List, Dict


def get_failed_ingestion_runs(db_path: str = "warehouse.duckdb") -> List[Dict]:
    query = """
        SELECT
            run_id,
            status,
            start_time,
            end_time,
            rows_loaded
        FROM ingestion_runs
        WHERE status = 'failed'
        ORDER BY start_time DESC
        LIMIT 10
    """

    try:
        con = duckdb.connect(db_path)
        result = con.execute(query).fetchall()
        columns = [desc[0] for desc in con.description]

        return [
            dict(zip(columns, row))
            for row in result
        ]

    except Exception as e:
        return [{"error": str(e)}]