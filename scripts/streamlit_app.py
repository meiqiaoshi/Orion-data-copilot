"""
Streamlit UI for Orion Data Copilot — same planner + executor as the CLI.

Run from the repository root:

    streamlit run scripts/streamlit_app.py
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure `import app.*` works when launched via `streamlit run scripts/...`
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.executor import execute_plan
from app.planner import plan_query
from app.schemas import ExecutionResult, PlanResult, UserQuery
from app.version import __version__


def _init_history() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _serialize_plan(plan: PlanResult) -> dict[str, Any]:
    return _json_safe(asdict(plan))


def _serialize_execution(ex: ExecutionResult) -> dict[str, Any]:
    return _json_safe(asdict(ex))


def main() -> None:
    _init_history()
    st.set_page_config(page_title="Orion Data Copilot", layout="wide")
    st.title("Orion Data Copilot")
    st.caption(f"Version {__version__} · same engine as `main.py`")

    with st.sidebar:
        st.header("Options")
        use_llm = st.toggle("Use LLM planner (OpenAI)", value=True)
        st.markdown(
            "Requires `OPENAI_API_KEY` when enabled. "
            "Turn off to match `python main.py --no-llm` (rules only)."
        )
        st.divider()
        st.subheader("Recent runs")
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            q = item["query"]
            preview = q if len(q) <= 60 else q[:60] + "..."
            with st.expander(f"{len(st.session_state.history) - i}. {preview}"):
                st.caption(f"Planner: {item['planner']} · {item['intent']} / {item['action']}")
                st.text(item["output"][:2000])

    query = st.text_area(
        "Natural language query",
        height=100,
        placeholder="e.g. Show failed ingestion jobs in the last 7 days",
    )
    run = st.button("Plan & execute", type="primary")

    if run and query.strip():
        uq = UserQuery(raw_text=query.strip())
        with st.spinner("Planning..."):
            plan = plan_query(uq, use_llm=use_llm)
        with st.spinner("Executing..."):
            execution = execute_plan(plan)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Plan")
            st.json(_serialize_plan(plan))
        with c2:
            st.subheader("Execution")
            st.json(_serialize_execution(execution))

        st.subheader("Output")
        st.markdown(execution.output)

        st.session_state.history.append(
            {
                "query": query.strip(),
                "planner": plan.planner_source,
                "intent": plan.intent,
                "action": plan.action,
                "output": execution.output,
            }
        )


if __name__ == "__main__":
    main()
