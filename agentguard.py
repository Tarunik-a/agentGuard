import json
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator


class ActionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["create_task", "delete_task", "view_task"]
    title: str | None = None
    priority: Literal["high", "medium", "low"] | None = None
    task_id: str | None = None

    @model_validator(mode="after")
    def validate_action_fields(self):

        if self.action == "create_task":
            if not self.title or not self.priority:
                raise ValueError("create_task requires title and priority")

        elif self.action in ["view_task", "delete_task"]:
            if not self.task_id:
                raise ValueError(f"{self.action} requires task_id")

        return self


# AGENTGUARD - STRUCTURED REPORT

# 1. Expected task
expected = {"action": "delete_task", "task_id": "task-123"}

proposed = {"action": "delete_task", "task_id": "task-123"}

# 3. User details
user_role = "Admin"

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
    if not intent_valid or not permission_valid or risk == "UNKNOWN":
        decision = "BLOCK"

    elif risk == "HIGH":
        decision = "REVIEW_REQUIRED"

    else:
        decision = "ALLOW"

        # 7. Explain the decision
    if not intent_valid:
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
        "schema_valid": True,
        "intent_valid": intent_valid,
        "permission_valid": permission_valid,
        "risk": risk,
        "decision": decision,
        "reason": reason,
        "errors": [],
    }


risk_levels = {"create_task": "MEDIUM", "delete_task": "HIGH", "view_task": "LOW"}

# 4. Application storage
tasks = []
verification_store = {}


def create_task(title, priority):

    task = {"id": str(uuid.uuid4()), "title": title, "priority": priority}

    tasks.append(task)
    verification_store[task["id"]] = task.copy()

    return task


def view_task(task_id):

    for task in tasks:
        if task["id"] == task_id:
            return task

    return None


def delete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            verification_store.pop(task_id, None)
            return task

    return None


def get_task_from_storage(task_id):
    task = verification_store.get(task_id)

    if task is not None:
        return task.copy()

    return None


def execute_task(expected, proposed):

    execution_status = "NOT_EXECUTED"
    verification_status = "NOT_CHECKED"
    errors = []
    evidence = []
    verification_messages = []

    try:
        action = proposed["action"]

        if action == "create_task":
            actual = create_task(proposed["title"], proposed["priority"])

        elif action == "view_task":
            actual = view_task(proposed["task_id"])

        elif action == "delete_task":
            actual = delete_task(proposed["task_id"])

        else:
            raise ValueError("Unsupported action")

        if actual is None:
            raise ValueError("Task not found")

        execution_status = "SUCCESS"

        verified, verification_errors, evidence, verification_messages = verify_state(
            expected, actual
        )

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
        "evidence": evidence,
        "verification_messages": verification_messages,
    }


def verify_state(expected, actual):

    errors = []
    evidence = []
    verification_messages = []
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        errors.append("Expected and actual results must be dictionaries")
        verification_messages.append("Verification failed: invalid input data.")
        return False, errors, evidence, verification_messages
    action = expected.get("action")
    task_id = expected.get("task_id")

    if action == "create_task":
        if not actual.get("id"):
            errors.append("Created task is missing its ID")
            verification_messages.append(
                "Verification failed: created task has no valid ID."
            )

        else:
            stored_task = get_task_from_storage(actual["id"])

            evidence.append(
                {
                    "check": "task_storage_lookup",
                    "task_id": actual["id"],
                    "found": stored_task is not None,
                    "data_matches": stored_task == actual
                    if stored_task is not None
                    else False,
                }
            )

            if stored_task is None:
                errors.append("Created task was not found in storage")
                verification_messages.append(
                    "Verification failed: created task was not found in storage."
                )

            elif stored_task != actual:
                errors.append("Stored task does not match created task")
                verification_messages.append(
                    "Verification failed: stored task data does not match the execution result."
                )
            else:
                verification_messages.append("Created task matches the stored task.")

        if expected.get("title") != actual.get("title"):
            errors.append("title is incorrect")
            verification_messages.append(
                "Verification failed: task title does not match the expected title."
            )

        if expected.get("priority") != actual.get("priority"):
            errors.append("priority is incorrect")
            verification_messages.append(
                "Verification failed: task priority does not match the expected priority."
            )

    elif action == "view_task":
        stored_task = get_task_from_storage(task_id)
        evidence.append(
            {
                "check": "task_storage_lookup",
                "task_id": task_id,
                "found": stored_task is not None,
                "data_matches": stored_task == actual
                if stored_task is not None
                else False,
            }
        )

        if stored_task is None:
            errors.append("Viewed task was not found in storage")
            verification_messages.append(
                "Verification failed: viewed task was not found in storage."
            )

        elif stored_task != actual:
            errors.append("Viewed task does not match stored task")
            verification_messages.append(
                "Verification failed: viewed task data does not match stored data."
            )

        else:
            verification_messages.append("Viewed task matches the stored task.")

    elif action == "delete_task":
        stored_task = get_task_from_storage(task_id)
        evidence.append(
            {
                "check": "task_deletion_lookup",
                "task_id": task_id,
                "still_exists": stored_task is not None,
                "deleted": stored_task is None,
            }
        )

        if stored_task is not None:
            errors.append("Deleted task still exists in storage")
            verification_messages.append(
                "Verification failed: deleted task still exists in storage."
            )

        else:
            verification_messages.append("Deleted task was not found in storage.")

    else:
        errors.append("Unsupported action for verification")
        verification_messages.append("Verification failed: unsupported action.")

    return len(errors) == 0, errors, evidence, verification_messages


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

    if not isinstance(report["record_id"], str):
        return {"saved": False, "error": "Audit report record_id must be a string"}

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

    if "execution" not in report:
        return {"saved": False, "error": "Audit report is missing execution"}

    if report["execution"] not in ["SUCCESS", "FAILED", "NOT_EXECUTED"]:
        return {"saved": False, "error": "Audit report has an invalid execution status"}

    if "verification" not in report:
        return {"saved": False, "error": "Audit report is missing verification"}

    if report["verification"] not in ["PASSED", "FAILED", "NOT_CHECKED"]:
        return {
            "saved": False,
            "error": "Audit report has an invalid verification status",
        }

    try:
        serialized_report = json.dumps(report)

        with open(file_path, "a") as file:
            file.write(serialized_report + "\n")

        return {"saved": True, "error": None}
    except (OSError, TypeError, ValueError) as error:
        return {"saved": False, "error": str(error)}


def main():
    result = evaluate_action(expected, proposed, user_role)
    schema_valid = result["schema_valid"]

    intent_valid = result["intent_valid"]
    permission_valid = result["permission_valid"]
    risk = result["risk"]
    decision = result["decision"]
    reason = result["reason"]
    execution_result = {"evidence": []}

    # 11. Execution

    if decision == "ALLOW":
        execution_result = execute_task(expected, proposed)

        execution_status = execution_result["execution"]
        verification_status = execution_result["verification"]
        errors = execution_result["errors"]

    elif decision == "REVIEW_REQUIRED":
        print("\nHuman approval required for this action.")

        approval = input("Approve this action? (yes/no): ").strip().lower()

        if approval == "yes":
            execution_result = execute_task(expected, proposed)

            execution_status = execution_result["execution"]
            verification_status = execution_result["verification"]
            errors = execution_result["errors"]

        else:
            execution_status = "NOT_EXECUTED"
            verification_status = "NOT_CHECKED"
            errors = ["Human review rejected the action"]

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
        "verification_summary": (
            "All verification checks passed"
            if verification_status == "PASSED"
            else "Verification was not successful"
        ),
        "evidence": execution_result.get("evidence", []),
        "verification_messages": execution_result.get("verification_messages", []),
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

    if audit_result["saved"]:
        report["audit_status"] = "SAVED"
    else:
        report["audit_status"] = "FAILED"

    report["audit_status"] = "SAVED" if audit_result["saved"] else "FAILED"

    if report["audit_status"] == "SAVED":
        print("\nAudit record saved successfully.")
    else:
        print("\nAudit record could not be saved.")
        print("Reason:", audit_result["error"])


if __name__ == "__main__":
    main()
