from app.executor import execute_plan
from app.planner import plan_query
from app.schemas import UserQuery


def main() -> None:
    print("Orion Data Copilot")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Query> ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        query = UserQuery(raw_text=user_input)
        plan = plan_query(query)
        execution = execute_plan(plan)

        print("\n--- Plan ---")
        print(f"Intent: {plan.intent}")
        print(f"Action: {plan.action}")
        print(f"Message: {plan.message}")

        print("\n--- Execution ---")
        print(f"Status: {execution.status}")
        print(f"Source: {execution.source}")
        print(f"Output: {execution.output}")
        print("-----------------\n")


if __name__ == "__main__":
    main()