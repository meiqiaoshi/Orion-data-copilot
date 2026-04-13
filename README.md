# Orion Data Copilot

Natural-language interface for querying **data platform metadata**: pipeline runs (IngestFlow / DuckDB) and data-quality signals (SentinelDQ). The system turns a plain-English question into a structured plan, runs the right connector, and prints a readable summary.

For design details, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Example prompts are in [`docs/USE_CASES.md`](docs/USE_CASES.md).

## What it does

- **Planner**: Tries an **LLM** (OpenAI) first, then falls back to **rule-based** classification (`app/planner.py`).
- **Execution**: Routes to **IngestFlow** metadata in DuckDB (`ingestion_runs`) or **SentinelDQ** alerts (`app/executor.py`).
- **Output**: Formatted text for failures, recent runs, or DQ alerts (`app/formatter.py`).

## Requirements

- **Python 3.10+** recommended (code uses modern typing; project has been used with 3.9+).
- Dependencies used by the app:
  - **duckdb** — query `warehouse.duckdb` (IngestFlow run history).
  - **openai** — optional; enables the LLM planner. Without it, only the rule planner runs.
  - **sentineldq** — optional; required for data-quality queries (`query_sentineldq_issues`).

Install (example):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install duckdb openai
# pip install sentineldq   # if you have the package and want DQ queries
```

If you add a non-empty `requirements.txt` later, you can replace the line above with `pip install -r requirements.txt`.

## Configuration

- **LLM planner**: Set `OPENAI_API_KEY` in your environment. The default model name is configured in `app/llm_planner.py` (`plan_query_with_llm`).
- **IngestFlow / DuckDB**: Connectors default to `warehouse.duckdb` in the current working directory. Ensure that file exists and contains an `ingestion_runs` table (e.g. from running [IngestFlow](https://github.com/meiqiaoshi/Ingestflow) pipelines).
- **SentinelDQ**: Must be importable and configured as expected by `sentineldq.metadata.store.get_recent_alerts` for DQ queries to succeed.

## Run

From the repository root:

```bash
python main.py
```

Type natural language questions at the `Query>` prompt. Use `exit` or `quit` to leave.

## Project layout

| Path | Role |
|------|------|
| `main.py` | CLI loop: read query → plan → execute → print |
| `app/planner.py` | LLM + rule planning |
| `app/executor.py` | Dispatch to connectors |
| `app/connectors/ingestflow.py` | DuckDB queries |
| `app/connectors/sentineldq.py` | SentinelDQ alerts |
| `app/llm_planner.py` | OpenAI Responses API → JSON plan |
| `app/time_parser.py`, `app/entity_parser.py` | Heuristic time/entity extraction for rules |
