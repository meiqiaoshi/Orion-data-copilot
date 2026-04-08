def plan_query(user_input: str) -> dict:
    text = user_input.lower()

    if "failed" in text or "failure" in text:
        return {
            "intent": "pipeline_failure_lookup",
            "action": "query_ingestion_runs",
            "message": "This query looks like a request to inspect failed pipeline runs."
        }

    if "quality" in text or "unhealthy" in text:
        return {
            "intent": "data_quality_lookup",
            "action": "query_sentineldq",
            "message": "This query looks like a request to inspect data quality issues."
        }

    return {
        "intent": "unknown",
        "action": "clarify_or_fallback",
        "message": "I could not confidently classify this query yet."
    }