from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from app.agent import agent
from app.agentt.clarification_manager import check_request
from app.agentt.state import AgentState
from app.database.database import initialize_database


THREAD_ID = "personal-assistant-session"

CONFIG: RunnableConfig = {
    "configurable": {
        "thread_id": THREAD_ID,
    }
}


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

        if state["current_action"] == "waiting_for_approval":
            result = agent.invoke(
                Command(resume=user_input),
                CONFIG,
            )

            interrupts = result.get("__interrupt__", [])

            if interrupts:
                approval_data = interrupts[0].value

                print(
                    f"\nAssistant: {approval_data['message']}"
                )

                continue

            state["current_action"] = "finished"

            if result.get("messages"):
                last_message = result["messages"][-1]

                print(
                    f"\nAssistant: {last_message.content}"
                )

                state["final_response"] = last_message.content

            continue

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

            message = (
                f"Complete the {intent} request "
                f"using this information: {data}"
            )

            state["messages"].append(
                {
                    "role": "user",
                    "content": message,
                }
            )

            state["current_action"] = "resuming_pending_action"

            agent_input = HumanMessage(
                content=message
            )

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

            agent_input = HumanMessage(
                content=user_input
            )

        result = agent.invoke(
            {
                "messages": [agent_input],
            },
            CONFIG,
        )

        interrupts = result.get("__interrupt__", [])

        if interrupts:
            approval_data = interrupts[0].value

            state["current_action"] = "waiting_for_approval"

            print(
                f"\nAssistant: {approval_data['message']}"
            )

            continue

        state["current_action"] = "finished"

        if result.get("messages"):
            last_message = result["messages"][-1]

            print(
                f"\nAssistant: {last_message.content}"
            )

            state["final_response"] = last_message.content


if __name__ == "__main__":
    main()