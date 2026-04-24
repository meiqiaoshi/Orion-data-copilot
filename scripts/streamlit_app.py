"""
Streamlit UI for Orion Data Copilot — same planner + executor as the CLI.

Run from the repository root:

    streamlit run scripts/streamlit_app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure `import app.*` works when launched via `streamlit run scripts/...`
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.executor import execute_plan
from app.json_serialization import execution_result_to_dict, plan_result_to_dict
from app.planner import plan_query
from app.remote_query import call_v1_query
from app.schemas import UserQuery
from app.version import __version__


def _init_history() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []


def main() -> None:
    _init_history()
    st.set_page_config(page_title="Orion Data Copilot", layout="wide")
    st.title("Orion Data Copilot")
    st.caption(f"Version {__version__} · same engine as `main.py`")

    api_base = os.environ.get("ORION_API_BASE", "").strip().rstrip("/")
    check_ready = os.environ.get("ORION_API_CHECK_READY", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    with st.sidebar:
        st.header("Options")
        if api_base:
            st.info(
                f"**Remote API:** `{api_base}` (`POST /v1/query`). "
                "Set `ORION_API_KEY` if the server requires it. "
                "Optional: `ORION_API_CHECK_READY=1` to `GET /ready` before each call."
            )
        use_llm = st.toggle("Use LLM planner (OpenAI)", value=True)
        st.markdown(
            "Requires `OPENAI_API_KEY` when enabled. "
            "Turn off to match `python main.py --no-llm` (rules only).\n\n"
            "In remote mode, the API server must have keys for planning/execution; "
            "this app only sends the natural-language query to `ORION_API_BASE`."
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
        text = query.strip()
        if api_base:
            try:
                with st.spinner("Calling API..."):
                    plan_dict, exec_dict = call_v1_query(
                        api_base, text, use_llm, check_ready=check_ready
                    )
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Plan")
                    st.json(plan_dict)
                with c2:
                    st.subheader("Execution")
                    st.json(exec_dict)
                st.subheader("Output")
                out = str(exec_dict.get("output", ""))
                st.markdown(out)
                st.session_state.history.append(
                    {
                        "query": text,
                        "planner": str(plan_dict.get("planner_source", "")),
                        "intent": str(plan_dict.get("intent", "")),
                        "action": str(plan_dict.get("action", "")),
                        "output": out,
                    }
                )
        else:
            uq = UserQuery(raw_text=text)
            with st.spinner("Planning..."):
                plan = plan_query(uq, use_llm=use_llm)
            with st.spinner("Executing..."):
                execution = execute_plan(plan)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Plan")
                st.json(plan_result_to_dict(plan))
            with c2:
                st.subheader("Execution")
                st.json(execution_result_to_dict(execution))

            st.subheader("Output")
            st.markdown(execution.output)

            st.session_state.history.append(
                {
                    "query": text,
                    "planner": plan.planner_source,
                    "intent": plan.intent,
                    "action": plan.action,
                    "output": execution.output,
                }
            )


if __name__ == "__main__":
    main()
