import json

from agentguard import (
    ActionSchema,
    check_permission,
    create_task,
    evaluate_action,
    execute_task,
    tasks,
    save_audit_record,
    verify_state,
)


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
    expected = {"action": "delete_task", "task_id": "task-123"}

    proposed = {"action": "delete_task", "task_id": "task-123"}

    result = evaluate_action(expected, proposed, "Viewer")

    assert result["decision"] == "BLOCK"

    assert result["reason"] == "User does not have permission"


def test_high_risk_action_requires_review():
    expected = {"action": "delete_task", "task_id": "task-123"}

    proposed = {"action": "delete_task", "task_id": "task-123"}

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


def test_execution_failure_is_recorded():

    execution_status = "NOT_EXECUTED"
    errors = []

    try:
        raise RuntimeError("Simulated application failure")

    except Exception as error:
        execution_status = "FAILED"
        errors.append(str(error))

    assert execution_status == "FAILED"
    assert "Simulated application failure" in errors


def test_create_task_executes_successfully():

    tasks.clear()

    result = create_task("Fix Login API", "high")

    assert result["title"] == "Fix Login API"
    assert result["priority"] == "high"
    assert result in tasks


def test_create_task_failure_with_invalid_arguments():

    tasks.clear()

    try:
        create_task()
        assert False, "Missing arguments should cause failure"

    except TypeError:
        assert True


def test_execute_task_handles_missing_fields():

    proposed = {"action": "create_task"}

    expected = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    result = execute_task(expected, proposed)

    assert result["execution"] == "FAILED"
    assert result["verification"] == "NOT_CHECKED"
    assert len(result["errors"]) > 0


def test_execute_task_detects_wrong_result(monkeypatch):

    import agentguard

    def wrong_create_task(title, priority):
        return {"title": "Wrong Task", "priority": priority}

    monkeypatch.setattr(agentguard, "create_task", wrong_create_task)

    expected = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    proposed = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

    result = agentguard.execute_task(expected, proposed)

    assert result["execution"] == "SUCCESS"
    assert result["verification"] == "FAILED"
    assert result["execution"] == "SUCCESS"
    assert "title is incorrect" in result["errors"]


def test_outcome_detects_verification_failure():

    from agentguard import determine_outcome

    outcome = determine_outcome("SUCCESS", "FAILED")

    assert outcome == "VERIFICATION_FAILED"


def test_successful_outcome():
    from agentguard import determine_outcome

    assert determine_outcome("SUCCESS", "PASSED") == "SUCCESS"


def test_execution_failed_outcome():
    from agentguard import determine_outcome

    assert determine_outcome("FAILED", "NOT_CHECKED") == "EXECUTION_FAILED"


def test_not_completed_outcome():
    from agentguard import determine_outcome

    assert determine_outcome("NOT_EXECUTED", "NOT_CHECKED") == "NOT_COMPLETED"


def test_audit_record_contains_outcome(tmp_path):

    import json

    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"

    report = {
        "record_id": "test-001",
        "execution": "SUCCESS",
        "verification": "FAILED",
        "outcome": "VERIFICATION_FAILED",
        "audit_status": "PENDING",
        "decision": "ALLOW",
    }

    save_audit_record(report, audit_file)

    with open(audit_file, "r") as file:
        saved_record = json.loads(file.readline())

    assert saved_record["outcome"] == "VERIFICATION_FAILED"
    assert saved_record["record_id"] == "test-001"
    assert saved_record["audit_status"] == "PENDING"


def test_audit_log_preserves_multiple_records(tmp_path):

    import json

    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"

    first_report = {
        "record_id": "test-001",
        "outcome": "SUCCESS",
        "decision": "ALLOW",
        "execution": "SUCCESS",
        "verification": "PASSED",
    }

    second_report = {
        "record_id": "test-002",
        "outcome": "VERIFICATION_FAILED",
        "decision": "ALLOW",
        "execution": "SUCCESS",
        "verification": "PASSED",
    }

    save_audit_record(first_report, audit_file)
    save_audit_record(second_report, audit_file)

    with open(audit_file, "r") as file:
        records = [json.loads(line) for line in file]

    assert len(records) == 2
    assert records[0]["record_id"] == "test-001"
    assert records[1]["record_id"] == "test-002"


def test_audit_save_handles_invalid_path(tmp_path):

    from agentguard import save_audit_record

    invalid_path = tmp_path / "missing_folder" / "audit_log.jsonl"

    report = {"record_id": "test-003", "outcome": "SUCCESS"}

    result = save_audit_record(report, invalid_path)

    assert result["saved"] is False
    assert result["error"] is not None


def test_audit_rejects_non_dictionary_report(tmp_path):

    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"

    result = save_audit_record("invalid report", audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report must be a dictionary"
    assert not audit_file.exists()


def test_audit_rejects_missing_record_id(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"outcome": "SUCCESS"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report is missing record_id"
    assert not audit_file.exists()


def test_audit_rejects_empty_record_id(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "", "outcome": "SUCCESS"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report has an empty record_id"
    assert not audit_file.exists()


def test_audit_rejects_non_string_record_id(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": 123, "outcome": "SUCCESS"}


def test_audit_rejects_whitespace_record_id(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "   ", "outcome": "SUCCESS"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report has an empty record_id"
    assert not audit_file.exists()


def test_audit_rejects_missing_outcome(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "test-001"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report is missing outcome"
    assert not audit_file.exists()


def test_audit_rejects_invalid_outcome(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "test-002", "outcome": "MAYBE"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report has an invalid outcome"
    assert not audit_file.exists()


def test_audit_rejects_missing_decision(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "test-003", "outcome": "SUCCESS"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report is missing decision"
    assert not audit_file.exists()


def test_audit_rejects_invalid_decision(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "test-004", "outcome": "SUCCESS", "decision": "MAYBE"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report has an invalid decision"
    assert not audit_file.exists()


def test_audit_rejects_missing_execution(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {"record_id": "test-005", "outcome": "SUCCESS", "decision": "ALLOW"}

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report is missing execution"
    assert not audit_file.exists()


def test_audit_rejects_invalid_execution_status(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {
        "record_id": "test-006",
        "outcome": "SUCCESS",
        "decision": "ALLOW",
        "execution": "MAYBE",
    }

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report has an invalid execution status"
    assert not audit_file.exists()


def test_audit_rejects_missing_verification(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"
    report = {
        "record_id": "test-007",
        "outcome": "SUCCESS",
        "decision": "ALLOW",
        "execution": "SUCCESS",
    }

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report is missing verification"
    assert not audit_file.exists()


def test_audit_rejects_invalid_verification_status(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"

    report = {
        "record_id": "test-008",
        "outcome": "SUCCESS",
        "decision": "ALLOW",
        "execution": "SUCCESS",
        "verification": "MAYBE",
    }

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] == "Audit report has an invalid verification status"
    assert not audit_file.exists()


def test_audit_handles_json_serialization_error(tmp_path):
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"

    report = {
        "record_id": "test-009",
        "outcome": "SUCCESS",
        "decision": "ALLOW",
        "execution": "SUCCESS",
        "verification": "PASSED",
        "extra_data": object(),
    }

    result = save_audit_record(report, audit_file)

    assert result["saved"] is False
    assert result["error"] is not None
    assert not audit_file.exists()


def test_audit_saves_valid_report(tmp_path):
    import json
    from agentguard import save_audit_record

    audit_file = tmp_path / "audit_log.jsonl"

    report = {
        "record_id": "test-010",
        "outcome": "SUCCESS",
        "decision": "ALLOW",
        "execution": "SUCCESS",
        "verification": "PASSED",
    }

    result = save_audit_record(report, audit_file)

    assert result["saved"] is True
    assert result["error"] is None

    saved_report = json.loads(audit_file.read_text())

    assert saved_report == report


def test_view_task_successfully():

    from agentguard import create_task, view_task, tasks

    tasks.clear()

    task = create_task("AgentGuard", "high")

    result = view_task(task["id"])

    assert result == task


def test_delete_task_successfully():

    from agentguard import create_task, delete_task, view_task, tasks

    tasks.clear()

    task = create_task("AgentGuard", "high")

    result = delete_task(task["id"])

    assert result == task
    assert view_task(task["id"]) is None


def test_delete_nonexistent_task():

    from agentguard import delete_task, tasks

    tasks.clear()

    result = delete_task("nonexistent-id")

    assert result is None
    assert tasks == []


def test_view_nonexistent_task():

    from agentguard import view_task, tasks

    tasks.clear()

    result = view_task("nonexistent-id")

    assert result is None
    assert tasks == []


def test_execute_view_task_successfully():

    from agentguard import create_task, execute_task, tasks

    tasks.clear()

    task = create_task("AgentGuard", "high")

    expected = {"action": "view_task", "task_id": task["id"]}

    proposed = expected.copy()

    result = execute_task(expected, proposed)

    assert result["execution"] == "SUCCESS"
    assert result["verification"] == "PASSED"
    assert result["errors"] == []


def test_execute_delete_task_successfully():

    from agentguard import create_task, execute_task, view_task, tasks

    tasks.clear()

    task = create_task("AgentGuard", "high")

    expected = {"action": "delete_task", "task_id": task["id"]}

    proposed = expected.copy()

    result = execute_task(expected, proposed)

    assert result["execution"] == "SUCCESS"
    assert result["verification"] == "PASSED"
    assert result["errors"] == []
    assert view_task(task["id"]) is None


def test_execute_view_nonexistent_task():

    import agentguard

    agentguard.tasks.clear()

    expected = {"action": "view_task", "task_id": "missing-task"}

    proposed = {"action": "view_task", "task_id": "missing-task"}

    result = agentguard.execute_task(expected, proposed)

    assert result["execution"] == "FAILED"
    assert result["verification"] == "NOT_CHECKED"
    assert "Task not found" in result["errors"]


def test_execute_delete_nonexistent_task():

    import agentguard

    agentguard.tasks.clear()

    expected = {"action": "delete_task", "task_id": "missing-task"}

    proposed = {"action": "delete_task", "task_id": "missing-task"}

    result = agentguard.execute_task(expected, proposed)

    assert result["execution"] == "FAILED"
    assert result["verification"] == "NOT_CHECKED"
    assert "Task not found" in result["errors"]


def test_execute_delete_detects_false_success(monkeypatch):

    task = create_task("Test Task", "high")

    def fake_delete_task(task_id):
        return task.copy()

    monkeypatch.setattr("agentguard.delete_task", fake_delete_task)

    expected = {"action": "delete_task", "task_id": task["id"]}

    proposed = expected.copy()

    result = execute_task(expected, proposed)

    assert result["execution"] == "SUCCESS"
    assert result["verification"] == "FAILED"
    assert "Deleted task still exists in storage" in result["errors"]


def test_execute_create_returns_verification_evidence():

    expected = {"action": "create_task", "title": "Evidence Test", "priority": "high"}

    proposed = expected.copy()

    result = execute_task(expected, proposed)

    assert result["verification"] == "PASSED"
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["check"] == "task_storage_lookup"
    assert result["evidence"][0]["found"] is True


def test_execute_view_returns_verification_evidence():

    task = create_task("View Evidence Test", "medium")

    expected = {"action": "view_task", "task_id": task["id"]}

    proposed = expected.copy()

    result = execute_task(expected, proposed)

    assert result["verification"] == "PASSED"
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["check"] == "task_storage_lookup"
    assert result["evidence"][0]["found"] is True


def test_execute_delete_returns_verification_evidence():

    task = create_task("Delete Evidence Test", "high")

    expected = {"action": "delete_task", "task_id": task["id"]}

    proposed = expected.copy()

    result = execute_task(expected, proposed)

    assert result["verification"] == "PASSED"
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["check"] == "task_deletion_lookup"
    assert result["evidence"][0]["still_exists"] is False


def test_audit_record_preserves_verification_evidence(tmp_path):

    report = {
        "record_id": "evidence-test-001",
        "decision": "ALLOW",
        "execution": "SUCCESS",
        "verification": "PASSED",
        "outcome": "SUCCESS",
        "evidence": [
            {"check": "task_storage_lookup", "task_id": "task-123", "found": True}
        ],
        "verification_messages": ["Created task was found and matches stored data."],
    }

    file_path = tmp_path / "audit.jsonl"

    result = save_audit_record(report, str(file_path))

    assert result["saved"] is True

    saved_report = json.loads(file_path.read_text())

    assert saved_report["evidence"] == report["evidence"]
    assert saved_report["verification_messages"] == report["verification_messages"]


def test_create_task_verification_failure_message(monkeypatch):

    actual = {"id": "task-123", "title": "Test task", "priority": "high"}

    monkeypatch.setattr("agentguard.get_task_from_storage", lambda task_id: None)

    expected = {"action": "create_task", "title": "Test task", "priority": "high"}

    verified, errors, evidence, messages = verify_state(expected, actual)

    assert verified is False
    assert "Created task was not found in storage" in errors
    assert any("Verification failed" in message for message in messages)


def test_view_task_verification_failure_message(monkeypatch):

    monkeypatch.setattr("agentguard.get_task_from_storage", lambda task_id: None)

    expected = {"action": "view_task", "task_id": "task-123"}

    actual = None

    verified, errors, evidence, messages = verify_state(expected, actual)

    assert verified is False
    assert "Viewed task was not found in storage" in errors
    assert any("Verification failed" in message for message in messages)


def test_delete_task_verification_failure_message(monkeypatch):

    monkeypatch.setattr(
        "agentguard.get_task_from_storage",
        lambda task_id: {"id": task_id, "title": "Test task", "priority": "high"},
    )

    expected = {"action": "delete_task", "task_id": "task-123"}

    actual = {"id": "task-123", "title": "Test task", "priority": "high"}

    verified, errors, evidence, messages = verify_state(expected, actual)

    assert verified is False
    assert "Deleted task still exists in storage" in errors
    assert any("Verification failed" in message for message in messages)
