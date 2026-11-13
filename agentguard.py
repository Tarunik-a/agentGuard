import json
from datetime import datetime

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

risk_levels = {"create_task": "MEDIUM", "delete_task": "HIGH", "view_task": "LOW"}

# 4. Application storage
tasks = []


# 5. Intent validation
intent_valid = expected == proposed

# 6. Permission validation
permission_valid = proposed["action"] in permissions.get(user_role, [])

# 7. Risk evaluation
risk = risk_levels.get(proposed["action"], "UNKNOWN")

# 8. Decision
if not intent_valid or not permission_valid or risk == "UNKNOWN":
    decision = "BLOCK"

elif risk == "HIGH":
    decision = "REVIEW_REQUIRED"

else:
    decision = "ALLOW"


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
