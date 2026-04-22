# Orion Data Copilot — Architecture Overview

---

## 🎯 System Goal

Orion Data Copilot is an AI-powered interface for querying data platform metadata using natural language.

It allows users to ask questions about:

- Pipeline execution (IngestFlow)
- Data quality signals (SentinelDQ)

and returns structured, human-readable insights.

---

## 🧠 Core Design Philosophy

The system is designed around three principles:

1. Separation of concerns
   - Query understanding, execution, and formatting are decoupled

2. Hybrid intelligence
   - Combines LLM-based planning with rule-based fallback

3. Composable architecture
   - Each component can be extended independently

---

## 🏗️ High-Level Architecture

User Query
   ↓
Planner (LLM + Rule-based fallback)
   ↓
Execution Plan (intent + filters)
   ↓
Executor (routing layer)
   ↓
Connectors (data sources)
   ↓
Formatter (AI-style response)

---

## 🔍 Component Breakdown

### Query Interface
- **CLI** (`main.py` / `orion-copilot`): interactive prompt; flags such as `--no-llm`, `--version`, and `--duckdb` (IngestFlow DB path)
- **Optional Streamlit UI** (`scripts/streamlit_app.py`): same planner and executor as the CLI; install via `requirements-ui.txt`
- **Optional HTTP API** (`app/api.py`, FastAPI + Uvicorn): `POST /v1/plan` (plan JSON only), `POST /v1/query` (plan + execution); OpenAPI at `/docs`; optional shared secret `ORION_API_KEY` via `app/api_auth.py`; install via `requirements-api.txt` or `pip install -e ".[api]"`

### Planner Layer
- LLM Planner (OpenAI)
- Rule-based fallback
- Outputs structured plan

### Execution Layer
- Routes queries to connectors

### Connectors
- IngestFlow (DuckDB; default `warehouse.duckdb`, override with env **`ORION_DUCKDB_PATH`**)
- SentinelDQ (Python package `sentineldq`; alerts via `get_recent_alerts`, typically backed by a local SQLite metadata DB)

### Formatter Layer
- Produces human-readable output
- Highlights key insights

### Error Handling
- Handles missing tables, DB errors, dependency issues
- Provides user-friendly messages

---

## 🔁 Example Data Flow

User query:
Show failed ingestion jobs for sample.yaml in the last 7 days

Flow:
1. Planner extracts intent + filters
2. Executor routes to connector
3. Connector queries metadata store
4. Formatter generates response

---

## 📊 Observability

- Tracks planner source (llm vs rules)
- Enables debugging and evaluation

---

## 🎯 MVP Scope

- Multi-source querying
- Hybrid planning
- Structured execution pipeline
- AI-style output

---

## 🚀 Future Directions

**Already in the repo (beyond the original MVP sketch):**
- Heuristic **root-cause style** reporting (`analyze_pipeline_failure`): failed IngestFlow runs plus ranked SentinelDQ alerts (time window, scoring)
- Baseline **Streamlit** UI for ad-hoc queries (not a full product portal)
- Baseline **HTTP API** (FastAPI) for programmatic access and integrations (`POST /v1/plan`, `POST /v1/query`, OpenAPI `/docs`)

**Still ahead:**
- Open-ended **NL → SQL** against arbitrary schemas (not fixed connector intents)
- **Richer** web experience (auth, saved contexts, collaboration) beyond the Streamlit prototype
- **Multi-step** reasoning and stronger causal diagnosis than keyword/time heuristics

---

## 💡 Key Takeaways

- AI + data engineering hybrid system
- Modular architecture
- Real-world metadata integration
