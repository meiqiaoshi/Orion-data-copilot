# Orion Data Copilot

[![CI](https://github.com/meiqiaoshi/Orion-data-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/meiqiaoshi/Orion-data-copilot/actions/workflows/ci.yml)

Natural-language interface for querying **data platform metadata**: pipeline runs (IngestFlow / DuckDB) and data-quality signals (SentinelDQ). The system turns a plain-English question into a structured plan, runs the right connector, and prints a readable summary.

For design details, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Example prompts are in [`docs/USE_CASES.md`](docs/USE_CASES.md).

## What it does

- **Planner**: Tries an **LLM** (OpenAI) first, then falls back to **rule-based** classification (`app/planner.py`).
- **Execution**: Routes to **IngestFlow** metadata in DuckDB (`ingestion_runs`) or **SentinelDQ** alerts (`app/executor.py`).
- **Output**: Formatted text for failures, recent runs, or DQ alerts (`app/formatter.py`).

Planning produces a **fixed set of intents** wired to connector queries; it does **not** generate arbitrary SQL for ad-hoc schemas.

## Status (vs. earlier roadmap)

**Shipped in this repo:** Interactive **CLI**; optional **Streamlit** UI and optional **HTTP API** (FastAPI in `app/api.py`) — **`POST /v1/query`** runs the same hybrid planner (OpenAI + rules) and connectors as the CLI; **`POST /v1/plan`** returns a plan JSON only (no connector calls); execution paths for **failed / recent IngestFlow runs** (DuckDB) and **SentinelDQ alerts** (when the package is available); **heuristic root-cause style** summaries that combine failed runs with **ranked** DQ matches (time window + scoring); basic **formatting** of those results.

**Still future work** (see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — *Future Directions*): open-ended **NL → SQL**, a fuller **product-style** web app, **multi-step** reasoning, and **stronger** causal diagnosis than heuristic matching. The old README listed some of these as “planned”; not all are implemented yet.

## Requirements

- **Python 3.10+** recommended (code uses modern typing; project has been used with 3.9+).
- Dependencies used by the app:
  - **duckdb** — query IngestFlow run history (default file `warehouse.duckdb`, or path from **`ORION_DUCKDB_PATH`**).
  - **openai** — optional; enables the LLM planner. Without it, only the rule planner runs.
  - **sentineldq** — optional; required for data-quality queries (`query_sentineldq_issues`).

Install (example):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# pip install sentineldq   # if you have the package and want DQ queries
```

Editable install from the repo root exposes the **`orion-copilot`** CLI (same as `python main.py`; version comes from `app/version.py`):

```bash
pip install -e .
orion-copilot --version
# pip install -e ".[ui]"    # optional: Streamlit (same pins as requirements-ui.txt)
# pip install -e ".[api]"   # optional: FastAPI + Uvicorn (HTTP API; see below)
# pip install -e ".[dev]"   # optional: pytest, ruff, pre-commit, httpx
```

For tests and lint (`pytest`, `ruff`; Ruff settings in `pyproject.toml`):

```bash
pip install -e ".[dev,api]"
# or: pip install -r requirements-dev.txt && pip install -r requirements-api.txt
ruff check app tests main.py scripts
pytest
```

Shortcuts (same shell must use your project Python, e.g. conda env `dev`):

```bash
make install-dev   # same as pip install -e ".[dev,api]"
make lint
make test
# make api           # uvicorn app.api:app (install [api] first)
# make docker-build  # needs Docker; then make docker-run
# make compose-up    # docker compose up --build (see docker-compose.yml)
```

See [`CHANGELOG.md`](CHANGELOG.md) for a coarse history of shipped features.

GitHub **CI** uses `pip install -e ".[dev,api]"` so every run checks packaging, the **`orion-copilot`** entry point, and the **HTTP API** test suite (FastAPI + Uvicorn). A second job **validates `docker compose`**, **builds the Docker image**, and hits **`/health`** in a short-lived container.

Some tests build a **temporary DuckDB** with an `ingestion_runs` schema (see `tests/test_ingestflow_integration.py`); they do not use your real `warehouse.duckdb`.

On GitHub, the **CI** workflow can also be triggered manually (**Actions → CI → Run workflow**) because `workflow_dispatch` is enabled.

Optional — run Ruff on `git commit` (same paths as CI):

```bash
pip install pre-commit   # or: already in requirements-dev.txt
pre-commit install
pre-commit run --all-files   # once, to verify hooks
```

## Configuration

- **LLM planner**: Set `OPENAI_API_KEY` in your environment. The default model name is configured in `app/llm_planner.py` (`plan_query_with_llm`).
- **IngestFlow / DuckDB**: Default file is `warehouse.duckdb` in the current working directory. Override with **`ORION_DUCKDB_PATH`** (absolute or relative path) for containers or non-default layouts, or pass **`--duckdb PATH`** on the CLI for one session. The file must exist and contain an `ingestion_runs` table (e.g. from running [IngestFlow](https://github.com/meiqiaoshi/Ingestflow) pipelines).
- **SentinelDQ**: Must be importable and configured as expected by `sentineldq.metadata.store.get_recent_alerts` for DQ queries to succeed.
- **HTTP API / Compose**: Optional shared secret **`ORION_API_KEY`** (see HTTP API section). For `docker compose`, copy [`.env.example`](.env.example) to `.env` if you want keys loaded from a file.

## Run

From the repository root:

```bash
python main.py
```

Use `python main.py --version` to print the CLI version (defined in `app/version.py`). Use `python main.py --no-llm` to force the **English keyword rule planner** only (no OpenAI), which matches local tests with `use_llm=False`. Use **`python main.py --duckdb /path/to/warehouse.duckdb`** to set **`ORION_DUCKDB_PATH`** for this process (same as the env var; `orion-copilot` supports it too).

Type natural language questions at the `Query>` prompt. Use `exit` or `quit` to leave.

## Web UI (Streamlit, optional)

Install UI dependencies (adds Streamlit on top of `requirements.txt`):

```bash
pip install -r requirements-ui.txt
```

From the repository root:

```bash
streamlit run scripts/streamlit_app.py
```

The sidebar toggles **LLM vs rules-only** planning (same behavior as `python main.py --no-llm` when disabled). Recent queries appear in the sidebar for quick reference.

## HTTP API (FastAPI, optional)

Install API dependencies:

```bash
pip install -r requirements-api.txt
# or: pip install -e ".[api]"
```

Run from the repository root (auto-generated OpenAPI UI at **http://127.0.0.1:8000/docs**):

```bash
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

- **POST `/v1/plan`** — same JSON body as below; returns **`plan` only** (no connector calls — useful for previews and avoiding DuckDB/SentinelDQ work).
- **POST `/v1/query`** — JSON body `{"query": "<natural language>", "use_llm": true}` → JSON with `plan` and `execution` (same structure as the Streamlit JSON panels; datetimes as ISO strings).
- **GET `/health`**, **GET `/v1/version`**, **GET `/`** — liveness and metadata (`/health` and `/` stay unauthenticated even when an API key is configured).
- **Optional auth:** set **`ORION_API_KEY`** in the environment. When set, **`/v1/plan`**, **`/v1/query`**, and **`/v1/version`** require header **`X-API-Key: <key>`** or **`Authorization: Bearer <key>`**. Omit the variable for local development (no key required).
- **CORS** is open (`allow_origins=["*"]`) for local and tooling; tighten behind a reverse proxy in production.
- **Tracing:** every response includes **`X-Request-ID`** (UUID unless the client sends a non-empty **`X-Request-ID`** header, which is echoed back). Listed in **`Access-Control-Expose-Headers`** for browser clients.

### Docker (HTTP API image)

From the repository root:

```bash
docker build -t orion-data-copilot .
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=... \
  -e ORION_API_KEY=... \
  -v /path/on/host/warehouse.duckdb:/app/warehouse.duckdb \
  orion-data-copilot
```

Working directory in the container is `/app`, which matches the default DuckDB path `warehouse.duckdb`. Mount your real metadata file as shown (or rely on images that already ship a DB). Omit `ORION_API_KEY` if you want an open `/v1` surface inside a trusted network only.

**Compose (optional):** copy [`.env.example`](.env.example) to `.env` and adjust keys, ensure `./warehouse.duckdb` exists (or comment out the `volumes` block in [`docker-compose.yml`](docker-compose.yml)), then:

```bash
docker compose up --build
```

Open **http://127.0.0.1:8000/docs**. Compose passes `OPENAI_API_KEY`, `ORION_API_KEY`, and **`ORION_DUCKDB_PATH`** (default **`/app/warehouse.duckdb`** in the file, matching the volume mount) from your shell or a root `.env` used for interpolation.

## Project layout

| Path | Role |
|------|------|
| `Dockerfile` | Container image for the FastAPI API (`uvicorn` on port 8000) |
| `docker-compose.yml` | Local `docker compose up` for the API + DuckDB mount |
| `.env.example` | Template for `OPENAI_API_KEY` / `ORION_API_KEY` (copy to `.env`) |
| `.dockerignore` | Keeps `docker build` context small |
| `Makefile` | Optional: `make lint`, `make test`, `make install-dev`, `make api`, `docker-build` / `docker-run` / `compose-up` |
| `CHANGELOG.md` | High-level feature history |
| `pyproject.toml` | Build / package metadata; Ruff settings; `orion-copilot` console script |
| `main.py` | CLI loop: read query → plan → execute → print |
| `app/version.py` | Single source for `__version__` (used by `--version`) |
| `app/planner.py` | LLM + rule planning |
| `app/executor.py` | Dispatch to connectors |
| `app/config.py` | e.g. `ORION_DUCKDB_PATH` resolution for IngestFlow |
| `app/connectors/ingestflow.py` | DuckDB queries |
| `app/connectors/sentineldq.py` | SentinelDQ alerts |
| `app/llm_planner.py` | OpenAI Responses API → JSON plan |
| `app/time_parser.py`, `app/entity_parser.py` | Heuristic time/entity extraction for rules |
| `app/json_serialization.py` | Plan/execution → JSON-safe dicts (API, Streamlit) |
| `app/api.py` | Optional FastAPI app (`uvicorn app.api:app`) |
| `app/api_auth.py` | Optional `ORION_API_KEY` check for `/v1/*` |
| `app/api_middleware.py` | `X-Request-ID` middleware |
| `scripts/streamlit_app.py` | Optional Streamlit UI (plan + execute + formatted output) |
| `requirements-api.txt` | FastAPI + Uvicorn for the HTTP API |
