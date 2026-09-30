from app.agent import agent
from app.database.database import initialize_database


def main():
    initialize_database()

    print("Personal AI Assistant")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        for message in result["messages"]:
            print("\n--- MESSAGE ---")
            print(f"Type: {type(message).__name__}")
            print(f"Content: {message.content}")

            if hasattr(message, "tool_calls"):
                print(f"Tool Calls: {message.tool_calls}")


if __name__ == "__main__":
    main()