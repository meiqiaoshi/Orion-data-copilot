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
- CLI-based input (main.py)
- Entry point of the system

### Planner Layer
- LLM Planner (OpenAI)
- Rule-based fallback
- Outputs structured plan

### Execution Layer
- Routes queries to connectors

### Connectors
- IngestFlow (DuckDB)
- SentinelDQ (SQLite API)

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

- Root cause analysis
- LLM SQL generation
- Web UI
- Multi-step reasoning

---

## 💡 Key Takeaways

- AI + data engineering hybrid system
- Modular architecture
- Real-world metadata integration
