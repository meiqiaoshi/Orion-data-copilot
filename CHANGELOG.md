# Changelog

All notable changes to this project are documented here. The format is loosely inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- **`GET /ready`** readiness probe: **`200`** when the configured DuckDB path is readable or can be created (`duckdb_runtime_ready` in `app/config.py`); **`503`** otherwise. Same auth rules as **`/health`** (no API key).
- CI **`test-fast`** job (Python 3.12, `pytest -m "not integration"`); Docker smoke test also curls **`/ready`**.
- OpenAPI description documents **`429`** rate-limit JSON and **`/ready`** semantics.
- Pytest marker **`integration`** for DuckDB-backed ingestflow tests (`pytest.ini`, `tests/test_ingestflow_integration.py`); use `pytest -m "not integration"` for a faster local run.
- FastAPI HTTP API (`app/api.py`): `POST /v1/plan` (plan only), `POST /v1/query`, health/version routes, OpenAPI at `/docs` with documented **`ApiKeyHeader`** / **`BearerAuth`** schemes; **`X-Request-ID`** and optional **`orion.api.access`** request logs (`app/api_middleware.py`, **`ORION_API_ACCESS_LOG`**); per-IP **rate limits** on POST routes via **slowapi** (`ORION_API_RATE_LIMIT_POST`, `app/config.py`).
- Optional API protection via `ORION_API_KEY` (`app/api_auth.py`).
- Optional Streamlit UI (`scripts/streamlit_app.py`) and `requirements-ui.txt`; remote mode via **`ORION_API_BASE`** + `app/remote_query.py` calling `POST /v1/query`.
- PEP 621 packaging: `pip install -e .`, `orion-copilot` CLI, optional extras `[ui]`, `[api]`, `[dev]`.
- Shared JSON helpers for plan/execution (`app/json_serialization.py`).
- `Makefile` for common local commands (`lint`, `test`, `install-dev`, `api`).
- `Dockerfile` + `.dockerignore` for running the HTTP API in a container.
- **GHCR** publish workflow (`.github/workflows/publish-ghcr.yml`) for `docker pull` from GitHub Container Registry.
- `docker-compose.yml` and `.env.example` for local API + DuckDB mount.
- **`ORION_DUCKDB_PATH`** env var (via `app/config.py`) to point IngestFlow at any DuckDB file; Compose sets a container default.
- CLI **`--duckdb PATH`** on `main.py` / `orion-copilot` (sets `ORION_DUCKDB_PATH` for the session).
- **`ORION_OPENAI_MODEL`** env var (default `gpt-5`) for the LLM planner (`app/config.py` + `plan_query_with_llm`).

### Changed

- **GET `/health`** now includes **`version`** next to **`status`** (same value as `/v1/version` and `/`); liveness probes that only check HTTP 200 remain valid.
- CI installs with `pip install -e ".[dev,api]"` and verifies `orion-copilot --version`.
- CI runs a **Docker** job that validates `docker compose config`, builds the API image, and curls **`/health`** and **`/ready`** inside a container.
