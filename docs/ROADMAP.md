# Roadmap

---

## Phase 1 (Completed)
- CLI query interface
- Rule-based planner
- LLM planner
- Hybrid planning
- IngestFlow connector
- SentinelDQ connector
- AI-style formatting
- Error handling

---

## Phase 2 (In progress)

### Root Cause Analysis
**Shipped (heuristic MVP):**
- Link latest ingestion failures with SentinelDQ alerts (time window around failure, ranked scoring)
- Entity signals: `config_path`, `pipeline_name`, `dataset_name`; failure-run `config_path` stem for matching
- Human-readable RCA output (failure details, DQ window, scored alerts with short reasons)

**Next:**
- Richer causal explanations (beyond keyword/time heuristics)
- Optional cross-source joins when stable identifiers exist

### Improved LLM Planning
- Better entity extraction
- Few-shot prompting
- Plan validation

---

## Phase 3 (Future)

### HTTP API
**Shipped (baseline):** FastAPI app (`app/api.py`): `POST /v1/query`, `GET /health`, `GET /v1/version`; OpenAPI `/docs`; permissive CORS for development. Optional shared secret via **`ORION_API_KEY`** (`app/api_auth.py`). Dependencies: `requirements-api.txt` / `pip install -e ".[api]"`.

**Next:** rate limits, richer auth (OAuth / mTLS), and deployment hardening. A **Dockerfile** in the repo runs the same Uvicorn app in a container (see README).

### Web UI
**Shipped (baseline):** optional Streamlit app (`scripts/streamlit_app.py`), `requirements-ui.txt`; sidebar LLM toggle and recent-query history.

**Next:**
- Chat-style layout and richer session UX if we outgrow the prototype
- Persistence / sharing of runs (beyond Streamlit session state)

### Advanced Reasoning
- Multi-step queries
- Cross-source joins

### Alert Intelligence
- Summarization
- Prioritization
- Trend detection
