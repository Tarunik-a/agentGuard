import json
from datetime import datetime
from typing import Literal

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

    return {
        "schema_valid": schema_valid,
        "intent_valid": intent_valid,
        "permission_valid": permission_valid,
        "risk": risk,
        "decision": decision,
        "errors": validation_errors,
    }


risk_levels = {"create_task": "MEDIUM", "delete_task": "HIGH", "view_task": "LOW"}

# 4. Application storage
tasks = []


def main():
    result = evaluate_action(expected, proposed, user_role)

    intent_valid = result["intent_valid"]
    permission_valid = result["permission_valid"]
    risk = result["risk"]
    decision = result["decision"]

    # 9. Application function
    def create_task(title, priority):

        task = {"title": title, "priority": priority}

        tasks.append(task)

        return task

    # 10. State verification
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

    # 11. Execution
    execution_status = "NOT_EXECUTED"
    verification_status = "NOT_CHECKED"
    errors = []

    if decision == "ALLOW":
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

    # 12. Build structured report
    report = {
        "intent": "PASSED" if intent_valid else "FAILED",
        "permission": "ALLOWED" if permission_valid else "DENIED",
        "risk": risk,
        "decision": decision,
        "execution": execution_status,
        "verification": verification_status,
        "errors": errors,
    }

    # 13. Display report
    print("\n===== AGENTGUARD FINAL REPORT =====")

    for key, value in report.items():
        print(f"{key}: {value}")

    # Add timestamp to report
    report["timestamp"] = datetime.now().isoformat()

    # Save report to audit log
    with open("audit_log.jsonl", "a") as file:
        file.write(json.dumps(report) + "\n")

    print("\nAudit record saved successfully.")


if __name__ == "__main__":
    main()
