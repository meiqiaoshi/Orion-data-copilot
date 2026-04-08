from dataclasses import dataclass
from typing import Literal


IntentType = Literal[
    "pipeline_failure_lookup",
    "data_quality_lookup",
    "unknown",
]

ActionType = Literal[
    "query_ingestion_runs",
    "query_sentineldq",
    "clarify_or_fallback",
]


@dataclass(slots=True)
class UserQuery:
    raw_text: str


@dataclass(slots=True)
class PlanResult:
    intent: IntentType
    action: ActionType
    message: str