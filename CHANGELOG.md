# Changelog

All notable changes to this project are documented here. The format is loosely inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.3.0] - 2026-04-24

### Added

- **HTTP API** (`app/api.py`): Fast **`POST /v1/plan`** and **`POST /v1/query`**; **`GET /health`** (with **`version`**), **`GET /ready`** (DuckDB readiness, **`503`** when not usable), **`GET /v1/version`**; optional **`ORION_API_KEY`** (`app/api_auth.py`); **`X-Request-ID`**, CORS (**`ORION_CORS_ORIGINS`** allowlist or **`*`**), optional access logs (**`ORION_API_ACCESS_LOG`**), slowapi rate limits (**`ORION_API_RATE_LIMIT_POST`**). OpenAPI: **`security`** for Authorize in **`/docs`**, **`tags`** (**probes** / **v1** / **service**), **`401`** / **`429`** / **`503`** response models, **`/redoc`**, **`/openapi.json`** links on **`GET /`**.
- **Config & CLI**: **`ORION_DUCKDB_PATH`**, **`ORION_OPENAI_MODEL`**, **`cors_allow_origins()`**, **`duckdb_runtime_ready()`**; **`orion-copilot --duckdb`**; **`main.py`** alignment.
- **Streamlit** (`scripts/streamlit_app.py`): optional **`ORION_API_BASE`** remote **`POST /v1/query`** via **`app/remote_query.py`** (**`check_v1_ready`**, **`ORION_API_CHECK_READY`**).
- **Packaging & ops**: PEP 621 + **`[ui]`** / **`[api]`** / **`[dev]`** extras; **`Makefile`** (**`test-fast`**); **`Dockerfile`**, **`docker-compose.yml`**, **`.env.example`**; GHCR publish workflow; CI matrix, **`test-fast`** job, Docker smoke (**`/health`**, **`/ready`**).
- **Tests**: pytest **`integration`** marker for DuckDB ingestflow tests.

### Changed

- **`GET /health`** includes **`version`** alongside **`status`**.
- CI installs **`pip install -e ".[dev,api]"`**, runs Ruff, full pytest, and Docker validation.
