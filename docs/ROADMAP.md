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
**Shipped (baseline):** FastAPI app (`app/api.py`): `POST /v1/plan`, `POST /v1/query`, `GET /health` (status + version), `GET /v1/version`; OpenAPI `/docs`; permissive CORS for development; optional shared secret via **`ORION_API_KEY`** (`app/api_auth.py`); per-IP **slowapi** limits on the two POST routes (`ORION_API_RATE_LIMIT_POST`). Dependencies: `requirements-api.txt` / `pip install -e ".[api]"`.

**Next:** richer auth (OAuth / mTLS) and deployment hardening. **Dockerfile** + optional **GHCR** publish (see README and `publish-ghcr.yml`) ship the Uvicorn image.

### Web UI
**Shipped (baseline):** optional Streamlit app (`scripts/streamlit_app.py`), `requirements-ui.txt`; sidebar LLM toggle and recent-query history; optional remote mode via **`ORION_API_BASE`** (HTTP `POST /v1/query` through `app/remote_query.py`).

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
