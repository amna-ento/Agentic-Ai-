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
    
    
    
@tool
def update_task(
    task_id: int,
    title: str = "",
    description: str = "",
    due_date: str = "",
    status: str = "",
) -> str:
    """Update an existing task. Use this when the user wants to change a task's title, description, due date, or status."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,),
    )

    task = cursor.fetchone()

    if not task:
        connection.close()
        return f"Task {task_id} not found."

    updates = []
    values = []

    if title:
        updates.append("title = ?")
        values.append(title)

    if description:
        updates.append("description = ?")
        values.append(description)

    if due_date:
        updates.append("due_date = ?")
        values.append(due_date)

    if status:
        updates.append("status = ?")
        values.append(status)

    if not updates:
        connection.close()
        return "No changes were provided."

    values.append(task_id)

    cursor.execute(
        f"""
        UPDATE tasks
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        values,
    )

    connection.commit()
    connection.close()

    return f"Task {task_id} updated successfully."    


@tool
def delete_task(task_id: int) -> str:
    """Delete an existing task by its ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,),
    )

    task = cursor.fetchone()

    if not task:
        connection.close()
        return f"Task {task_id} not found."

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,),
    )

    connection.commit()
    connection.close()

    return f"Task {task_id} deleted successfully."


@tool
def complete_task(task_id: int) -> str:
    """Mark an existing task as completed."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,),
    )

    task = cursor.fetchone()

    if not task:
        connection.close()
        return f"Task {task_id} not found."

    cursor.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        """,
        ("completed", task_id),
    )

    connection.commit()
    connection.close()

    return f"Task {task_id} marked as completed."