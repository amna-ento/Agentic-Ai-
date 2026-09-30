from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from app.tools.calculator import calculate
from app.tools.datetime_tool import get_current_datetime
from app.tools.reminders import create_reminder
from app.tools.tasks import create_task
from app.tools.tasks import create_task, view_tasks
from app.tools.reminders import create_reminder, view_reminders


model = ChatOllama(
    model="qwen3:8b",
    temperature=0,
    reasoning=False,
)

agent = create_agent(
    model=model,
    tools=[
        calculate,
        get_current_datetime,
        create_task,
        view_tasks,
        view_reminders,
        create_reminder,
    ],
    system_prompt="You are a helpful personal AI assistant.",
)