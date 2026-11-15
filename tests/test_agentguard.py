from agentguard import check_permission, evaluate_action, ActionSchema


def test_admin_can_delete_task():
    assert check_permission("Admin", "delete_task") == True


def test_manager_can_create_task():
    assert check_permission("Manager", "create_task") == True


def test_viewer_cannot_create_task():
    assert check_permission("Viewer", "create_task") == False


def test_viewer_cannot_delete_task():
    assert check_permission("Viewer", "delete_task") == False


def test_unknown_role_is_denied():
    assert check_permission("Unknown", "create_task") == False


from agentguard import evaluate_action


def test_valid_manager_action():
    expected = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    proposed = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    result = evaluate_action(expected, proposed, "Manager")

    assert result["decision"] == "ALLOW"


def test_invalid_intent_is_blocked():
    expected = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    proposed = {"action": "create_task", "title": "Fix Login API", "priority": "low"}

    result = evaluate_action(expected, proposed, "Manager")

    assert result["decision"] == "BLOCK"


def test_unauthorized_action_is_blocked():
    expected = {"action": "delete_task"}

    proposed = {"action": "delete_task"}

    result = evaluate_action(expected, proposed, "Viewer")

    assert result["decision"] == "BLOCK"


def test_high_risk_action_requires_review():
    expected = {"action": "delete_task"}

    proposed = {"action": "delete_task"}

    result = evaluate_action(expected, proposed, "Admin")

    assert result["decision"] == "REVIEW_REQUIRED"


def test_missing_action_is_blocked():
    expected = {"action": "create_task"}
    proposed = {"title": "Fix Login API"}

    result = evaluate_action(expected, proposed, "Manager")

    assert result["decision"] == "BLOCK"


def test_none_proposal_is_blocked():
    expected = {"action": "create_task"}

    result = evaluate_action(expected, None, "Manager")

    assert result["decision"] == "BLOCK"


def test_valid_action_schema():
    proposal = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    validated = ActionSchema.model_validate(proposal)

    assert validated.priority == "high"


def test_invalid_priority_is_rejected():
    from pydantic import ValidationError

    proposal = {"action": "create_task", "title": "Fix Login API", "priority": "urgent"}

    try:
        ActionSchema.model_validate(proposal)
        assert False, "Invalid priority should be rejected"

    except ValidationError:
        assert True
