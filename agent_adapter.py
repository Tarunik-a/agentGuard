import json
from ollama import chat


def generate_action(user_request):

    try:
        response = chat(
            model="qwen2.5:3b",
            format="json",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You convert user instructions into structured task actions.

                    STRICT RULES:

                    1. Never invent or assume missing information.
                    2. Never use default titles or priorities.
                    3. For create_task, both title and priority
                    must be explicitly provided by the user.
                    4. For view_task and delete_task, task_id
                    must be explicitly provided by the user.
                    5. If any required information is missing,
                    return {"action": "invalid"}.
                    6. Do not generate unsupported actions.

                    Supported actions:
                    - create_task: title and priority required.
                    - view_task: task_id required.
                    - delete_task: task_id required.

                    Allowed priorities: high, medium, low.

                    Return only a valid JSON object containing:
                    action, title, priority, task_id.
                    """,
                },
                {"role": "user", "content": user_request},
            ],
        )

        proposed_action = json.loads(response.message.content)

    except Exception as e:
        print("AI Adapter Error:", e)
        return {"action": "invalid"}

    action = proposed_action.get("action")

    user_text = user_request.lower()

    explicit_priorities = ["high", "medium", "low"]

    has_explicit_priority = any(
        priority in user_text.split() for priority in explicit_priorities
    )

    if action == "create_task":
        if (
            not proposed_action.get("title")
            or not proposed_action.get("priority")
            or proposed_action.get("priority") not in ["high", "medium", "low"]
            or not has_explicit_priority
        ):
            return {"action": "invalid"}

    elif action in ["view_task", "delete_task"]:
        task_id = proposed_action.get("task_id")

        if not task_id:
            return {"action": "invalid"}

        if str(task_id).lower() not in user_text:
            return {"action": "invalid"}

    else:
        return {"action": "invalid"}

    if action == "create_task":
        return {
            "action": "create_task",
            "title": proposed_action["title"],
            "priority": proposed_action["priority"],
        }

    return {"action": action, "task_id": str(proposed_action["task_id"])}
