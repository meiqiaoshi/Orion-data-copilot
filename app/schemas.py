from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


IntentType = Literal[
    "pipeline_failure_lookup",
    "pipeline_run_lookup",
    "data_quality_lookup",
    "unknown",
]

ActionType = Literal[
    "query_ingestion_runs",
    "query_recent_ingestion_runs",
    "query_sentineldq",
    "clarify_or_fallback",
]

ExecutionStatus = Literal[
    "success",
    "not_implemented",
    "error",
]

SourceType = Literal[
    "ingestflow",
    "sentineldq",
    "system",
]


@dataclass(slots=True)
class UserQuery:
    raw_text: str


@dataclass(slots=True)
class TimeFilter:
    label: str
    start_time: datetime
    end_time: datetime


@dataclass(slots=True)
class EntityFilter:
    config_path: str | None = None
    pipeline_name: str | None = None


@dataclass(slots=True)
class PlanResult:
    intent: IntentType
    action: ActionType
    message: str
    time_filter: TimeFilter | None = None
    entity_filter: EntityFilter | None = None


@dataclass(slots=True)
class ExecutionResult:
    status: ExecutionStatus
    source: SourceType
    output: str