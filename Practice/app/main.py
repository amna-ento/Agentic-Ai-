from app.agent import agent
from app.agentt.clarification_manager import check_request
from app.agentt.state import AgentState
from app.database.database import initialize_database


def main():
    initialize_database()

    print("Personal AI Assistant")
    print("Type 'exit' or 'quit' to stop.")

    state: AgentState = {
        "messages": [],
        "user_request": "",
        "tool_calls": [],
        "tool_results": [],
        "current_action": "",
        "pending_action": {},
        "final_response": "",
    }

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        state["user_request"] = user_input
        state["current_action"] = "processing request"

        if state["pending_action"]:
            pending_action = state["pending_action"]

            intent = pending_action["intent"]
            data = pending_action["data"]
            missing_fields = pending_action["missing_fields"]

            missing_field = missing_fields[0]

            data[missing_field] = user_input

            state["pending_action"] = {}

            state["messages"].append(
                {
                    "role": "user",
                    "content": (
                        f"Complete the {intent} request "
                        f"using this information: {data}"
                    ),
                }
            )

            state["current_action"] = "resuming_pending_action"

        else:
            state["messages"].append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            clarification = check_request(user_input)

            if clarification["missing_fields"]:
                state["pending_action"] = {
                    "intent": clarification["intent"],
                    "data": clarification["data"],
                    "missing_fields": clarification["missing_fields"],
                }

                state["current_action"] = "waiting_for_information"

                missing_field = clarification["missing_fields"][0]

                print(
                    f"\nAssistant: Please provide the "
                    f"{missing_field.replace('_', ' ')}."
                )

                continue

        previous_message_count = len(state["messages"])

        result = agent.invoke(
            {
                "messages": state["messages"]
            }
        )

        state["messages"] = result["messages"]

        new_messages = state["messages"][previous_message_count:]

        state["tool_calls"] = []
        state["tool_results"] = []

        for message in new_messages:
            print("\n--- MESSAGE ---")
            print(f"Type: {type(message).__name__}")
            print(f"Content: {message.content}")

            if hasattr(message, "tool_calls") and message.tool_calls:
                state["tool_calls"].extend(message.tool_calls)
                print(f"Tool Calls: {message.tool_calls}")

            if type(message).__name__ == "ToolMessage":
                state["tool_results"].append(message.content)

        state["current_action"] = "finished"

        if new_messages:
            last_message = new_messages[-1]

            if type(last_message).__name__ == "AIMessage":
                state["final_response"] = last_message.content


if __name__ == "__main__":
    main()