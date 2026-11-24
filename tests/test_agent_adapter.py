import json
from types import SimpleNamespace

from ollama import chat

import agent_adapter


def mock_chat_response(action):

    return SimpleNamespace(message=SimpleNamespace(content=json.dumps(action)))


def test_valid_create_task(monkeypatch):

    def fake_chat(**kwargs):

        return mock_chat_response(
            {"action": "create_task", "title": "Finish assignment", "priority": "high"}
        )

    monkeypatch.setattr(agent_adapter, "chat", fake_chat)
    result = agent_adapter.generate_action(
        "Create a high priority task called Finish assignment"
    )

    assert result == {
        "action": "create_task",
        "title": "Finish assignment",
        "priority": "high",
    }


def test_missing_priority_is_rejected(monkeypatch):

    def fake_chat(**kwargs):
        return mock_chat_response(
            {
                "action": "create_task",
                "title": "Finish assignment",
                "priority": "medium",
            }
        )

    monkeypatch.setattr("agent_adapter.chat", fake_chat)

    result = generate_action("Create a task called Finish assignment")

    assert result == {"action": "invalid"}


def test_unsupported_action_is_rejected(monkeypatch):

    def fake_chat(**kwargs):
        return mock_chat_response({"action": "send_email"})

    monkeypatch.setattr("agent_adapter.chat", fake_chat)

    result = generate_action("Send an email to my professor")

    assert result == {"action": "invalid"}


def test_missing_task_id_is_rejected(monkeypatch):

    def fake_chat(**kwargs):
        return mock_chat_response({"action": "view_task", "task_id": "unknown"})

    monkeypatch.setattr("agent_adapter.chat", fake_chat)

    result = generate_action("Show me a task")

    assert result == {"action": "invalid"}


def generate_action(user_request):

    try:
        response = chat(
            # your existing Ollama configuration
        )

        proposed_action = json.loads(response.message.content)

    except Exception:
        return {"action": "invalid"}

    # Keep the remaining existing validation code here
    action = proposed_action.get("action")

    user_text = user_request.lower()

    explicit_priorities = ["high", "medium", "low"]
