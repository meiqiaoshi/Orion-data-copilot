from app.planner import plan_query


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

        result = plan_query(user_input)

        print("\n--- Result ---")
        print(f"Intent: {result['intent']}")
        print(f"Action: {result['action']}")
        print(f"Message: {result['message']}")
        print("--------------\n")


if __name__ == "__main__":
    main()