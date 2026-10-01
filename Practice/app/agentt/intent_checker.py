from app.agent import model


def check_intent(user_request: str) -> str:
    prompt = f"""
Analyze the user's request and identify the intended action.

User request:
{user_request}

Return only one action from this list:
create_reminder
update_reminder
delete_reminder
complete_reminder
view_reminders
create_task
update_task
delete_task
complete_task
view_tasks
calculate
get_current_datetime
normal_question
"""

    response = model.invoke(prompt)

    return str(response.content).strip()


if __name__ == "__main__":
    request = input("Enter request: ")
    intent = check_intent(request)
    print(f"Detected intent: {intent}")