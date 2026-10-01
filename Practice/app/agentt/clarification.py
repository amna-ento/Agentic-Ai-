from app.agentt.state import AgentState


def clarification_node(state: AgentState) -> AgentState:
    user_request = state["user_request"].strip()

    lower_request = user_request.lower()

    if lower_request.startswith("remind me to"):
        reminder_title = user_request[len("remind me to"):].strip()

        if reminder_title:
            state["pending_action"] = f"create_reminder|{reminder_title}"
            state["current_action"] = "waiting_for_reminder_time"
            state["final_response"] = "What time should I remind you?"
            return state

    state["pending_action"] = ""
    state["current_action"] = "ready_for_execution"

    return state