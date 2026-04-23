"""HTTP API (FastAPI) — same planner and executor as the CLI and Streamlit UI."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.api_auth import verify_api_key_if_configured
from app.api_middleware import REQUEST_ID_HEADER, AccessLogMiddleware, RequestIdMiddleware
from app.config import api_post_rate_limit_spec
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

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_LIMIT_POST = api_post_rate_limit_spec()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[REQUEST_ID_HEADER],
)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AccessLogMiddleware)


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


@limiter.limit(_LIMIT_POST)
@app.post("/v1/plan", response_model=PlanResponse)
def plan_only(
    request: Request,
    req: QueryRequest,
    _: None = Depends(verify_api_key_if_configured),
) -> PlanResponse:
    """Plan only (no connector execution)."""
    uq = UserQuery(raw_text=req.query)
    plan = plan_query(uq, use_llm=req.use_llm)
    return PlanResponse(plan=plan_result_to_dict(plan))


@limiter.limit(_LIMIT_POST)
@app.post("/v1/query", response_model=QueryResponse)
def run_query(
    request: Request,
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


_OPENAPI_AUTH_BLURB = (
    "\n\n### Authentication\n"
    "When the server sets **`ORION_API_KEY`**, send **`X-API-Key`** or **`Authorization: Bearer "
    "<key>`** on **`/v1/plan`**, **`/v1/query`**, and **`/v1/version`**. "
    "If that variable is unset, those routes stay open (development default).\n\n"
    "### Rate limiting\n"
    "**`POST /v1/plan`** and **`POST /v1/query`** share a per-client limit (default **`60/minute`**). "
    "Override with **`ORION_API_RATE_LIMIT_POST`** using slowapi syntax (e.g. `120/minute`). "
    "Set to **`off`**, **`0`**, **`false`**, or **`none`** for an effectively unlimited cap."
)


def custom_openapi() -> dict[str, Any]:
    from fastapi.openapi.utils import get_openapi

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=str(app.version),
        openapi_version=app.openapi_version,
        description=(app.description or "") + _OPENAPI_AUTH_BLURB,
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {}).update(
        {
            "ApiKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Matches `ORION_API_KEY` when enabled on the server.",
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Alternative to X-API-Key when `ORION_API_KEY` is enabled.",
            },
        }
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]
