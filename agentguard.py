import json
from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator


class ActionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["create_task", "delete_task", "view_task"]
    title: str | None = None
    priority: Literal["high", "medium", "low"] | None = None

    @model_validator(mode="after")
    def validate_action_fields(self):

        if self.action == "create_task":
            if not self.title or not self.priority:
                raise ValueError("create_task requires title and priority")

        return self


# AGENTGUARD - STRUCTURED REPORT

# 1. Expected task
expected = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

# 2. AI proposal
proposed = {"action": "create_task", "title": "Fix Login API", "priority": "high"}

# 3. User details
user_role = "Manager"

permissions = {
    "Admin": ["create_task", "delete_task"],
    "Manager": ["create_task"],
    "Viewer": ["view_task"],
}


def check_permission(role, action):
    return action in permissions.get(role, [])


def evaluate_action(expected, proposed, role):

    # 1. Check whether inputs are dictionaries
    if not isinstance(expected, dict) or not isinstance(proposed, dict):
        return {
            "schema_valid": False,
            "intent_valid": False,
            "permission_valid": False,
            "risk": "UNKNOWN",
            "decision": "BLOCK",
            "errors": ["Input must be a dictionary"],
            "reason": "Input must be a dictionary",
        }

    # 2. Validate proposal using Pydantic
    try:
        validated = ActionSchema.model_validate(proposed)
        schema_valid = True
        validation_errors = []

    except ValidationError as error:
        return {
            "schema_valid": False,
            "intent_valid": False,
            "permission_valid": False,
            "risk": "UNKNOWN",
            "decision": "BLOCK",
            "reason": "Invalid action schema",
            "errors": error.errors(),
        }

    # 3. Check intent
    intent_valid = expected == proposed

    # 4. Check permission
    action = validated.action
    permission_valid = check_permission(role, action)

    # 5. Check risk
    risk = risk_levels.get(action, "UNKNOWN")

    # 6. Make decision
    if (
        not schema_valid
        or not intent_valid
        or not permission_valid
        or risk == "UNKNOWN"
    ):
        decision = "BLOCK"

    elif risk == "HIGH":
        decision = "REVIEW_REQUIRED"

    else:
        decision = "ALLOW"

        # 7. Explain the decision
    if not schema_valid:
        reason = "Invalid action schema"

    elif not intent_valid:
        reason = "Proposed action does not match expected intent"

    elif not permission_valid:
        reason = "User does not have permission"

    elif risk == "UNKNOWN":
        reason = "Unknown risk level"

    elif decision == "REVIEW_REQUIRED":
        reason = "High-risk action requires human review"

    else:
        reason = "All validation checks passed"

    return {
        "schema_valid": schema_valid,
        "intent_valid": intent_valid,
        "permission_valid": permission_valid,
        "risk": risk,
        "decision": decision,
        "reason": reason,
        "errors": validation_errors,
    }


risk_levels = {"create_task": "MEDIUM", "delete_task": "HIGH", "view_task": "LOW"}

# 4. Application storage
tasks = []


def create_task(title, priority):

    task = {"title": title, "priority": priority}

    tasks.append(task)

    return task


def execute_task(expected, proposed):

    execution_status = "NOT_EXECUTED"
    verification_status = "NOT_CHECKED"
    errors = []

    try:
        actual = create_task(proposed["title"], proposed["priority"])

        execution_status = "SUCCESS"

        verified, verification_errors = verify_state(expected, actual)

        if verified:
            verification_status = "PASSED"
        else:
            verification_status = "FAILED"
            errors.extend(verification_errors)

    except Exception as error:
        execution_status = "FAILED"
        errors.append(str(error))

    return {
        "execution": execution_status,
        "verification": verification_status,
        "errors": errors,
    }


def verify_state(expected, actual):

    errors = []

    for field in expected:
        if field == "action":
            continue

        if field not in actual:
            errors.append(field + " is missing")

        elif expected[field] != actual[field]:
            errors.append(field + " is incorrect")

    return len(errors) == 0, errors


def determine_outcome(execution_status, verification_status):

    if execution_status == "SUCCESS" and verification_status == "PASSED":
        return "SUCCESS"

    if verification_status == "FAILED":
        return "VERIFICATION_FAILED"

    if execution_status == "FAILED":
        return "EXECUTION_FAILED"

    return "NOT_COMPLETED"


def save_audit_record(report, file_path="audit_log.jsonl"):

    if not isinstance(report, dict):
        return {"saved": False, "error": "Audit report must be a dictionary"}

    if "record_id" not in report:
        return {"saved": False, "error": "Audit report is missing record_id"}

    if not report["record_id"].strip():
        return {"saved": False, "error": "Audit report has an empty record_id"}

    if "outcome" not in report:
        return {"saved": False, "error": "Audit report is missing outcome"}

    if report["outcome"] not in [
        "SUCCESS",
        "VERIFICATION_FAILED",
        "EXECUTION_FAILED",
        "NOT_COMPLETED",
    ]:
        return {"saved": False, "error": "Audit report has an invalid outcome"}

    if "decision" not in report:
        return {"saved": False, "error": "Audit report is missing decision"}

    if report["decision"] not in ["ALLOW", "BLOCK", "REVIEW_REQUIRED"]:
        return {"saved": False, "error": "Audit report has an invalid decision"}

    if not isinstance(report["record_id"], str):
        return {"saved": False, "error": "Audit report record_id must be a string"}
    try:
        with open(file_path, "a") as file:
            file.write(json.dumps(report) + "\n")

        return {"saved": True, "error": None}

    except OSError as error:
        return {"saved": False, "error": str(error)}


def main():
    result = evaluate_action(expected, proposed, user_role)
    schema_valid = result["schema_valid"]

    intent_valid = result["intent_valid"]
    permission_valid = result["permission_valid"]
    risk = result["risk"]
    decision = result["decision"]
    reason = result["reason"]

    # 11. Execution

    if decision == "ALLOW":
        execution_result = execute_task(expected, proposed)

        execution_status = execution_result["execution"]
        verification_status = execution_result["verification"]
        errors = execution_result["errors"]

    else:
        execution_status = "NOT_EXECUTED"
        verification_status = "NOT_CHECKED"
        errors = []

    # 12. Build structured report
    report = {
        "record_id": str(uuid.uuid4()),
        "schema": "PASSED" if schema_valid else "FAILED",
        "intent": "PASSED" if intent_valid else "FAILED",
        "permission": "ALLOWED" if permission_valid else "DENIED",
        "risk": risk,
        "decision": decision,
        "execution": execution_status,
        "verification": verification_status,
        "outcome": determine_outcome(execution_status, verification_status),
        "errors": errors,
        "reason": reason,
    }

    # 13. Display report
    print("\n===== AGENTGUARD FINAL REPORT =====")

    for key, value in report.items():
        print(f"{key}: {value}")

    # Add timestamp to report
    report["timestamp"] = datetime.now().isoformat()

    report["audit_status"] = "PENDING"

    # Save report to audit log
    audit_result = save_audit_record(report)

    report["audit_status"] = "SAVED" if audit_result["saved"] else "FAILED"

    print("\nAudit record saved successfully.")


if __name__ == "__main__":
    main()
