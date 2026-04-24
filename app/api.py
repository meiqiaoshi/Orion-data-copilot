"""HTTP API (FastAPI) — same planner and executor as the CLI and Streamlit UI."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.api_auth import verify_api_key_if_configured
from app.api_middleware import REQUEST_ID_HEADER, AccessLogMiddleware, RequestIdMiddleware
from app.config import api_post_rate_limit_spec, duckdb_runtime_ready, resolve_duckdb_path
from app.executor import execute_plan
from app.json_serialization import execution_result_to_dict, plan_result_to_dict
from app.planner import plan_query
from app.schemas import UserQuery
from app.version import __version__

_OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "probes",
        "description": "Liveness (`/health`) and readiness (`/ready`) for orchestration.",
    },
    {
        "name": "v1",
        "description": "Version, planning, and query execution over pipeline metadata.",
    },
    {
        "name": "service",
        "description": "Entry point and documentation links.",
    },
]

app = FastAPI(
    title="Orion Data Copilot",
    description="Natural-language queries against pipeline metadata (IngestFlow, SentinelDQ).",
    version=__version__,
    openapi_tags=_OPENAPI_TAGS,
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


class RateLimitErrorBody(BaseModel):
    """JSON body returned by slowapi when ``POST`` rate limits are exceeded."""

    error: str = Field(..., description='Typically begins with "Rate limit exceeded:".')


class ReadyResponse(BaseModel):
    status: Literal["ready"] = "ready"
    duckdb: str = Field(..., description="Resolved path from `ORION_DUCKDB_PATH` (or default).")


class HttpErrorBody(BaseModel):
    """JSON for FastAPI ``HTTPException`` (401, 503, etc.)."""

    detail: str


_READY_RESPONSES: dict[int | str, dict[str, Any]] = {
    503: {
        "description": "Configured DuckDB path is not available (readiness check failed).",
        "model": HttpErrorBody,
    },
}


_POST_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {
        "description": "Missing or invalid API key when `ORION_API_KEY` is set on the server.",
        "model": HttpErrorBody,
    },
    429: {
        "description": "Too many requests from this client IP (slowapi).",
        "model": RateLimitErrorBody,
    },
}

_V1_VERSION_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {
        "description": "Missing or invalid API key when `ORION_API_KEY` is set on the server.",
        "model": HttpErrorBody,
    },
}


@app.get("/health", tags=["probes"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/ready", response_model=ReadyResponse, responses=_READY_RESPONSES, tags=["probes"])
def ready() -> ReadyResponse:
    """Readiness: configured DuckDB path must exist and be readable, or be creatable."""
    ok, err = duckdb_runtime_ready(None)
    path = resolve_duckdb_path(None)
    if not ok:
        raise HTTPException(status_code=503, detail=err)
    return ReadyResponse(duckdb=path)


@app.get("/v1/version", responses=_V1_VERSION_RESPONSES, tags=["v1"])
def version_info(_: None = Depends(verify_api_key_if_configured)) -> dict[str, str]:
    return {"version": __version__}


@limiter.limit(_LIMIT_POST)
@app.post("/v1/plan", response_model=PlanResponse, responses=_POST_RESPONSES, tags=["v1"])
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
@app.post("/v1/query", response_model=QueryResponse, responses=_POST_RESPONSES, tags=["v1"])
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


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {
        "service": "orion-data-copilot",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
        "ready": "/ready",
        "plan": "POST /v1/plan",
        "query": "POST /v1/query",
    }


_OPENAPI_AUTH_BLURB = (
    "\n\n### Authentication\n"
    "When the server sets **`ORION_API_KEY`**, send **`X-API-Key`** or **`Authorization: Bearer "
    "<key>`** on **`/v1/plan`**, **`/v1/query`**, and **`/v1/version`**. "
    "If the key is missing or wrong, those routes return **`401`** with JSON "
    "**`{\"detail\": \"...\"}`**. "
    "If that variable is unset, those routes stay open (development default). "
    "Those operations still declare **OpenAPI `security`** (API key **or** bearer) so **`/docs`** "
    "offers **Authorize**; leave it empty when the server has no key configured.\n\n"
    "### Rate limiting\n"
    "**`POST /v1/plan`** and **`POST /v1/query`** share a per-client limit (default **`60/minute`**). "
    "Override with **`ORION_API_RATE_LIMIT_POST`** using slowapi syntax (e.g. `120/minute`). "
    "Set to **`off`**, **`0`**, **`false`**, or **`none`** for an effectively unlimited cap. "
    "When exceeded, the API returns **`429 Too Many Requests`** with JSON "
    "**`{\"error\": \"Rate limit exceeded: …\"}`** (slowapi) and may add rate-limit headers.\n\n"
    "### Readiness\n"
    "**`GET /ready`** returns **`200`** when the configured DuckDB file (from **`ORION_DUCKDB_PATH`** "
    "or default **`warehouse.duckdb`**) exists and is readable, or does not exist but its parent "
    "directory is writable so DuckDB can create it. Otherwise **`503`** with a **`detail`** string."
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
    openapi_schema["tags"] = list(_OPENAPI_TAGS)
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
    # OR semantics: satisfy ApiKeyHeader *or* BearerAuth (see OpenAPI 3 security array).
    _auth_security: list[dict[str, list[str]]] = [
        {"ApiKeyHeader": []},
        {"BearerAuth": []},
    ]
    for path, method in (("/v1/plan", "post"), ("/v1/query", "post"), ("/v1/version", "get")):
        op = openapi_schema.get("paths", {}).get(path, {}).get(method)
        if op is not None:
            op["security"] = _auth_security
    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]
