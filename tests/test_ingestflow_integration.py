from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import duckdb
import pytest

from app.connectors.ingestflow import get_failed_ingestion_runs, get_recent_ingestion_runs
from app.schemas import EntityFilter, TimeFilter


@pytest.fixture
def duckdb_path(tmp_path: Path) -> str:
    path = str(tmp_path / "test.duckdb")
    con = duckdb.connect(path)
    con.execute(
        """
        CREATE TABLE ingestion_runs (
            run_id VARCHAR,
            status VARCHAR,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            rows_loaded INTEGER,
            config_path VARCHAR
        )
        """
    )
    base = datetime(2026, 4, 16, 12, 0, 0)
    con.execute(
        """
        INSERT INTO ingestion_runs VALUES
        ('r-fail', 'failed', ?, ?, 0, 'configs/sample.yaml'),
        ('r-ok', 'success', ?, ?, 100, 'configs/sample.yaml')
        """,
        [
            base,
            base + timedelta(minutes=5),
            base + timedelta(hours=1),
            base + timedelta(hours=1, minutes=5),
        ],
    )
    con.close()
    return path


def test_get_failed_ingestion_runs_returns_only_failed(duckdb_path: str) -> None:
    rows = get_failed_ingestion_runs(db_path=duckdb_path, limit=10)
    assert len(rows) == 1
    assert rows[0]["run_id"] == "r-fail"
    assert rows[0]["status"] == "failed"


def test_get_failed_ingestion_runs_filter_by_config_path(duckdb_path: str) -> None:
    ef = EntityFilter(config_path="sample.yaml")
    rows = get_failed_ingestion_runs(db_path=duckdb_path, entity_filter=ef, limit=10)
    assert len(rows) == 1
    assert "sample" in (rows[0].get("config_path") or "")


def test_get_recent_ingestion_runs_orders_by_start_time(duckdb_path: str) -> None:
    rows = get_recent_ingestion_runs(db_path=duckdb_path, limit=10)
    assert len(rows) == 2
    assert rows[0]["run_id"] == "r-ok"
    assert rows[1]["run_id"] == "r-fail"


def test_get_failed_respects_time_filter(duckdb_path: str) -> None:
    tf = TimeFilter(
        label="window",
        start_time=datetime(2026, 4, 16, 11, 0, 0),
        end_time=datetime(2026, 4, 16, 12, 30, 0),
    )
    rows = get_failed_ingestion_runs(db_path=duckdb_path, time_filter=tf, limit=10)
    assert len(rows) == 1
    assert rows[0]["run_id"] == "r-fail"
