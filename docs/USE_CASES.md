# Use Cases

## Acceptance checklist (copy/paste)

Use these queries as a quick acceptance pass for the project. All queries work in the interactive CLI (`orion-copilot` / `python main.py`) and via the HTTP API (`POST /v1/plan`, `POST /v1/query`).

1. **Rules-only sanity check (no DuckDB / no SentinelDQ required)**
   - Query: `what is the weather`
   - Expected: intent `unknown` (stable fallback), readable response (no stacktrace)

2. **Failed runs (DuckDB / IngestFlow required)**
   - Query: `Show failed ingestion jobs in the last 7 days`
   - Expected intent: `query_ingestion_runs`

3. **Recent runs (DuckDB / IngestFlow required)**
   - Query: `Show recent ingestion runs for sample.yaml`
   - Expected intent: `query_recent_ingestion_runs`

4. **Root-cause style (DuckDB required; SentinelDQ optional but recommended)**
   - Query: `Why did pipeline orders fail yesterday?`
   - Expected intent: `analyze_pipeline_failure`

5. **Data quality alerts (SentinelDQ required)**
   - Query: `Any data quality alerts for dataset raw_orders?`
   - Expected intent: `query_sentineldq_issues`

6. **Plan-only endpoint does not execute connectors (API only)**
   - Call: `POST /v1/plan` with JSON `{"query":"Show failed ingestion jobs in the last 7 days","use_llm":false}`
   - Expected: response JSON has `{"plan": ...}` only (no `execution` section)

## Example 1 — Failed runs
**User:** Show failed ingestion jobs in the last 7 days  
**System:** `query_ingestion_runs` → IngestFlow `ingestion_runs` (DuckDB)  
**Output:** Formatted list of failed runs (with optional time/entity filters)

## Example 2 — Root-cause style (Phase 2)
**User:** Why did pipeline `orders` fail yesterday?  
**System:** `analyze_pipeline_failure` → failed runs + SentinelDQ alerts in a time window, ranked with short match reasons  
**Output:** Failure signal, `config_path`, DQ lookup window, ranked related alerts

## Example 3 — Recent runs
**User:** Show recent ingestion runs for `sample.yaml`  
**System:** `query_recent_ingestion_runs`  
**Output:** Recent run rows and summary text

## Example 4 — Data quality
**User:** Any data quality alerts for dataset `raw_orders`?  
**System:** `query_sentineldq_issues` → `get_recent_alerts` (when SentinelDQ is available)  
**Output:** Alert list / formatted summary
