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

    assert result["reason"] == "All validation checks passed"


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

    assert result["reason"] == "User does not have permission"


def test_high_risk_action_requires_review():
    expected = {"action": "delete_task"}

    proposed = {"action": "delete_task"}

    result = evaluate_action(expected, proposed, "Admin")

    assert result["decision"] == "REVIEW_REQUIRED"

    assert result["reason"] == "High-risk action requires human review"


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


def test_create_task_missing_title_is_rejected():

    proposal = {"action": "create_task", "priority": "high"}

    from pydantic import ValidationError

    try:
        ActionSchema.model_validate(proposal)
        assert False, "Missing title should be rejected"
    except ValidationError:
        assert True


def test_unexpected_field_is_rejected():

    proposal = {
        "action": "create_task",
        "title": "Fix Login API",
        "priority": "high",
        "password": "secret",
    }

    from pydantic import ValidationError

    try:
        ActionSchema.model_validate(proposal)
        assert False, "Unexpected field should be rejected"
    except ValidationError:
        assert True


def test_invalid_priority_type_is_rejected():

    proposal = {"action": "create_task", "title": "Fix Login API", "priority": 123}

    from pydantic import ValidationError

    try:
        ActionSchema.model_validate(proposal)
        assert False, "Invalid priority type should be rejected"
    except ValidationError:
        assert True


def test_invalid_schema_returns_reason():

    expected = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    proposed = {"action": "create_task", "title": "Fix Login API", "priority": "urgent"}

    result = evaluate_action(expected, proposed, "Manager")

    assert result["decision"] == "BLOCK"
    assert result["schema_valid"] is False
    assert result["reason"] == "Invalid action schema"
