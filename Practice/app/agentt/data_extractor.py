import json

from app.agent import model


def extract_data(user_request: str, intent: str) -> dict:
    prompt = f"""
Extract the information provided by the user.

Intent:
{intent}

User request:
{user_request}

Return only a valid JSON object.

For create_reminder:
{{
    "title": "",
    "reminder_time": ""
}}

For delete_reminder or complete_reminder:
{{
    "reminder_id": ""
}}

For create_task:
{{
    "title": ""
}}

For delete_task or complete_task:
{{
    "task_id": ""
}}

If information is not provided, use an empty string.
"""

    response = model.invoke(prompt)

    content = str(response.content).strip()

    return json.loads(content)



if __name__ == "__main__":
    request = input("Enter request: ")
    intent = input("Enter intent: ")

    data = extract_data(request, intent)

    print(f"Extracted data: {data}")