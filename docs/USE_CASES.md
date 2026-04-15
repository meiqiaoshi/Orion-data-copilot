# Use Cases

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
