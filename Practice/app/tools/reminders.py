from langchain_core.tools import tool

from app.database.database import get_connection


@tool
def create_reminder(
    title: str,
    reminder_time: str,
) -> str:
    """Create a new reminder with a title and reminder time."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO reminders (title, reminder_time, status)
        VALUES (?, ?, ?)
        """,
        (title, reminder_time, "pending"),
    )

    reminder_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return f"Reminder created successfully. Reminder ID: {reminder_id}"


@tool
def view_reminders() -> str:
    """View the user's reminders. Use this when the user asks to see, list, show, check, review, or know what reminders they have."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, reminder_time, status
        FROM reminders
        ORDER BY id
        """
    )

    reminders = cursor.fetchall()
    connection.close()

    if not reminders:
        return "No reminders found."

    return "\n".join(
        f"ID: {reminder[0]} | Title: {reminder[1]} | "
        f"Time: {reminder[2]} | Status: {reminder[3]}"
        for reminder in reminders
    )
    
    
@tool
def update_reminder(
    reminder_id: int,
    title: str = "",
    reminder_time: str = "",
    status: str = "",
) -> str:
    """Update an existing reminder's title, reminder time, or status."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM reminders WHERE id = ?",
        (reminder_id,),
    )

    reminder = cursor.fetchone()

    if not reminder:
        connection.close()
        return f"Reminder {reminder_id} not found."

    updates = []
    values = []

    if title:
        updates.append("title = ?")
        values.append(title)

    if reminder_time:
        updates.append("reminder_time = ?")
        values.append(reminder_time)

    if status:
        updates.append("status = ?")
        values.append(status)

    if not updates:
        connection.close()
        return "No changes were provided."

    values.append(reminder_id)

    cursor.execute(
        f"""
        UPDATE reminders
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        values,
    )

    connection.commit()
    connection.close()

    return f"Reminder {reminder_id} updated successfully."    


@tool
def delete_reminder(reminder_id: int) -> str:
    """Delete an existing reminder by its ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM reminders WHERE id = ?",
        (reminder_id,),
    )

    reminder = cursor.fetchone()

    if not reminder:
        connection.close()
        return f"Reminder {reminder_id} not found."

    cursor.execute(
        "DELETE FROM reminders WHERE id = ?",
        (reminder_id,),
    )

    connection.commit()
    connection.close()

    return f"Reminder {reminder_id} deleted successfully."


@tool
def complete_reminder(reminder_id: int) -> str:
    """Mark an existing reminder as completed."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM reminders WHERE id = ?",
        (reminder_id,),
    )

    reminder = cursor.fetchone()

    if not reminder:
        connection.close()
        return f"Reminder {reminder_id} not found."

    cursor.execute(
        """
        UPDATE reminders
        SET status = ?
        WHERE id = ?
        """,
        ("completed", reminder_id),
    )

    connection.commit()
    connection.close()

    return f"Reminder {reminder_id} marked as completed."

