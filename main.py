from __future__ import annotations

import argparse

from app.executor import execute_plan
from app.planner import plan_query
from app.schemas import UserQuery
from app.version import __version__


def main() -> None:
    parser = argparse.ArgumentParser(description="Orion Data Copilot CLI")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Use the rule-based planner only (skip OpenAI even if configured).",
    )
    args = parser.parse_args()
    use_llm = not args.no_llm

    print("Orion Data Copilot")
    if not use_llm:
        print("(Rule-based planner only — LLM disabled.)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Query> ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        query = UserQuery(raw_text=user_input)
        plan = plan_query(query, use_llm=use_llm)
        execution = execute_plan(plan)

        print("\n--- Plan ---")
        print(f"Planner: {plan.planner_source}")
        print(f"Intent: {plan.intent}")
        print(f"Action: {plan.action}")
        print(f"Message: {plan.message}")

        if plan.time_filter is not None:
            print(
                "Time Filter: "
                f"{plan.time_filter.label} "
                f"({plan.time_filter.start_time} -> {plan.time_filter.end_time})"
            )
        else:
            print("Time Filter: none")

        if plan.entity_filter is not None:
            print(
                "Entity Filter: "
                f"config_path={plan.entity_filter.config_path}, "
                f"pipeline_name={plan.entity_filter.pipeline_name}, "
                f"dataset_name={plan.entity_filter.dataset_name}"
            )
        else:
            print("Entity Filter: none")

        print("\n--- Execution ---")
        print(f"Status: {execution.status}")
        print(f"Source: {execution.source}")
        print(f"Output: {execution.output}")
        print("-----------------\n")


if __name__ == "__main__":
    main()