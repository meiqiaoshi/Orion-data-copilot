"""HTTP API (FastAPI) — same planner and executor as the CLI and Streamlit UI."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.api_auth import verify_api_key_if_configured
from app.api_middleware import REQUEST_ID_HEADER, RequestIdMiddleware
from app.executor import execute_plan
from app.json_serialization import execution_result_to_dict, plan_result_to_dict
from app.planner import plan_query
from app.schemas import UserQuery
from app.version import __version__

app = FastAPI(
    title="Orion Data Copilot",
    description="Natural-language queries against pipeline metadata (IngestFlow, SentinelDQ).",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[REQUEST_ID_HEADER],
)

app.add_middleware(RequestIdMiddleware)


class QueryRequest(BaseModel):
    query: str = Field(..., max_length=32000)
    use_llm: bool = True

    @field_validator("query")
    @classmethod
    def strip_nonempty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("query must not be empty")
        return s


class QueryResponse(BaseModel):
    plan: dict[str, Any]
    execution: dict[str, Any]


class PlanResponse(BaseModel):
    plan: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/version")
def version_info(_: None = Depends(verify_api_key_if_configured)) -> dict[str, str]:
    return {"version": __version__}


@app.post("/v1/plan", response_model=PlanResponse)
def plan_only(
    req: QueryRequest,
    _: None = Depends(verify_api_key_if_configured),
) -> PlanResponse:
    """Plan only (no connector execution)."""
    uq = UserQuery(raw_text=req.query)
    plan = plan_query(uq, use_llm=req.use_llm)
    return PlanResponse(plan=plan_result_to_dict(plan))


@app.post("/v1/query", response_model=QueryResponse)
def run_query(
    req: QueryRequest,
    _: None = Depends(verify_api_key_if_configured),
) -> QueryResponse:
    uq = UserQuery(raw_text=req.query)
    plan = plan_query(uq, use_llm=req.use_llm)
    execution = execute_plan(plan)
    return QueryResponse(
        plan=plan_result_to_dict(plan),
        execution=execution_result_to_dict(execution),
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "orion-data-copilot",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
        "plan": "POST /v1/plan",
        "query": "POST /v1/query",
    }
