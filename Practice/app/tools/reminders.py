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