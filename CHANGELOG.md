# Changelog

All notable changes to this project are documented here. The format is loosely inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- FastAPI HTTP API (`app/api.py`): `POST /v1/query`, health/version routes, OpenAPI at `/docs`.
- Optional API protection via `ORION_API_KEY` (`app/api_auth.py`).
- Optional Streamlit UI (`scripts/streamlit_app.py`) and `requirements-ui.txt`.
- PEP 621 packaging: `pip install -e .`, `orion-copilot` CLI, optional extras `[ui]`, `[api]`, `[dev]`.
- Shared JSON helpers for plan/execution (`app/json_serialization.py`).
- `Makefile` for common local commands (`lint`, `test`, `install-dev`, `api`).
- `Dockerfile` + `.dockerignore` for running the HTTP API in a container.
- `docker-compose.yml` and `.env.example` for local API + DuckDB mount.
- **`ORION_DUCKDB_PATH`** env var (via `app/config.py`) to point IngestFlow at any DuckDB file; Compose sets a container default.

### Changed

- CI installs with `pip install -e ".[dev,api]"` and verifies `orion-copilot --version`.
- CI runs a **Docker** job that validates `docker compose config`, builds the API image, and curls `/health` inside a container.
