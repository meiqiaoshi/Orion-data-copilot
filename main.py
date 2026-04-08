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
        result = plan_query(query)

        print("\n--- Result ---")
        print(f"Intent: {result.intent}")
        print(f"Action: {result.action}")
        print(f"Message: {result.message}")
        print("--------------\n")


if __name__ == "__main__":
    main()