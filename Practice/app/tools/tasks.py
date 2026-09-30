from langchain_core.tools import tool

from app.database.database import get_connection


@tool
def create_task(
    title: str,
    description: str = "",
    due_date: str = "",
) -> str:
    """Create a new task with a title, optional description, and optional due date."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, description, due_date, status)
        VALUES (?, ?, ?, ?)
        """,
        (title, description, due_date, "pending"),
    )

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return f"Task created successfully. Task ID: {task_id}"


@tool
def view_tasks() -> str:
    """View the user's tasks. Use this when the user asks to see, list, show, check, review, or know what tasks they have, including questions like 'What do I still need to do?' or 'What tasks do I have?'."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, description, due_date, status
        FROM tasks
        ORDER BY id
        """
    )

    tasks = cursor.fetchall()
    connection.close()

    if not tasks:
        return "No tasks found."

    return "\n".join(
        f"ID: {task[0]} | Title: {task[1]} | "
        f"Description: {task[2]} | Due: {task[3]} | Status: {task[4]}"
        for task in tasks
    )