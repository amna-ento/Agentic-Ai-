from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from app.memory.checkpointer import create_checkpointer
from langgraph.types import interrupt

from app.tools.calculator import calculate
from app.tools.datetime_tool import get_current_datetime
from app.tools.email import draft_email, send_email
from app.tools.memory import remember_memory, recall_memory

from app.tools.reminders import (
    create_reminder,
    view_reminders,
    update_reminder,
    delete_reminder,
    complete_reminder,
)

from app.tools.tasks import (
    create_task,
    view_tasks,
    update_task,
    delete_task,
    complete_task,
)


model = ChatOllama(
    model="qwen3:8b",
    temperature=0,
    reasoning=False,
)


@tool
def delete_task_with_approval(task_id: int) -> str:
    """Delete an existing task after getting human approval."""
    approval = interrupt(
        {
            "action": "delete_task",
            "task_id": task_id,
            "message": f"Approve deleting task {task_id}? (yes/no)",
        }
    )

    if str(approval).lower() not in {"yes", "y"}:
        return f"Deletion of task {task_id} cancelled."

    return delete_task.invoke({"task_id": task_id})


@tool
def send_email_with_approval(email: dict) -> str:
    """Send an email after getting human approval."""
    approval = interrupt(
        {
            "action": "send_email",
            "email": email,
            "message": (
                f"Approve sending this email?\n"
                f"To: {email['recipient']}\n"
                f"Subject: {email['subject']}\n"
                f"Body: {email['body']}\n"
                f"(yes/no)"
            ),
        }
    )

    if str(approval).lower() not in {"yes", "y"}:
        return "Email sending cancelled."

    send_email(email)

    return "Email sent successfully."


system_prompt = """
You are a helpful personal AI assistant.

Choose the appropriate tool based on the user's intent.

Tool routing rules:
- Use calculate for mathematical calculations.
- Use get_current_datetime when the user asks for the current date or time.

Task tools:
- Use create_task when the user wants to create or add a task.
- Use view_tasks when the user wants to see, list, check, or review tasks.
- Use update_task when the user wants to modify an existing task.
- Use delete_task_with_approval when the user wants to remove a task.
- Use complete_task when the user says a task is finished or should be marked completed.

Reminder tools:
- Use create_reminder when the user wants to create or set a reminder.
- Use view_reminders when the user wants to see, list, check, or review reminders.
- Use update_reminder when the user wants to modify an existing reminder.
- Use delete_reminder when the user wants to delete a reminder.
- Use complete_reminder when the user says a reminder is finished or should be marked completed.

Email tools:
- Use draft_email when the user wants to compose or send an email.
- Before sending an email, use draft_email to create the email data.
- After creating the draft, use send_email_with_approval to send it.
- Never send an email without human approval.
- Never call send_email directly.
- If the user wants to send an email but required information is missing, ask for the missing information first.
- Required email information is recipient, subject, and body.

Memory tools:
- Use remember_memory when the user explicitly asks you to remember, save, or store information for future conversations.
- Use recall_memory when the user asks what you remember about previously stored information.
- When recalling memory, use the user's question or relevant concept as the search query.
- Do not require the user to provide an exact memory key.
- Do not store every conversation message as memory.
- Only store information that the user explicitly wants remembered.
- Never invent or guess information to store.
- When saving a memory, choose a short descriptive key.

Examples:
- "Remember that I prefer formal emails."
  → remember_memory(key="email_style", value="formal")

- "Remember that my favorite programming language is Python."
  → remember_memory(key="favorite_programming_language", value="Python")

- "What is my favorite programming language?"
  → recall_memory(query="favorite programming language")

- "Which email style do I prefer?"
  → recall_memory(query="email style")

Missing information rules:
- Before calling a tool, check whether all required information is available.
- Never invent, guess, assume, or create a value for a required tool argument that the user did not provide.
- If required information is missing, do not call the tool.
- Ask the user specifically for the missing information.
- Remember the original request while waiting for the user's answer.
- When the user provides the missing information in a later message, use it to continue the original request.
- For create_reminder, both title and reminder_time are required.
- If the user asks to create a reminder but does not provide the reminder time, ask for the reminder time instead of assuming one.
- For delete_task, use delete_task_with_approval.

Do not use a tool when the user is only asking a normal question that does not require one.
"""


checkpointer = create_checkpointer()


agent = create_agent(
    model=model,
    tools=[
        calculate,
        get_current_datetime,
        create_task,
        view_tasks,
        update_task,
        delete_task_with_approval,
        complete_task,
        create_reminder,
        view_reminders,
        update_reminder,
        delete_reminder,
        complete_reminder,
        draft_email,
        send_email_with_approval,
        remember_memory,
        recall_memory,
    ],
    system_prompt=system_prompt,
    checkpointer=checkpointer,
)