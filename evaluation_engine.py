# AGENTGUARD - PROPOSAL TESTING

permissions = {
    "Admin": ["create_task", "update_task", "delete_task"],
    "Manager": ["create_task", "update_task"],
    "Viewer": ["view_task"],
}

risk_levels = {
    "create_task": "MEDIUM",
    "update_task": "MEDIUM",
    "delete_task": "HIGH",
    "view_task": "LOW",
}


def evaluate_action(expected, proposed, role):

    # Check intent
    intent_valid = expected == proposed

    # Check permission
    permission_valid = proposed.get("action") in permissions.get(role, [])

    # Check risk
    risk = risk_levels.get(proposed.get("action"), "UNKNOWN")

    # Generate decision
    if not intent_valid or not permission_valid or risk == "UNKNOWN":
        return "BLOCK"

    elif risk == "HIGH":
        return "REVIEW_REQUIRED"

    else:
        return "ALLOW"


# Test cases
test_cases = [
    {
        "name": "Correct proposal",
        "expected": {"action": "create_task", "priority": "high"},
        "proposed": {"action": "create_task", "priority": "high"},
        "role": "Manager",
        "expected_decision": "ALLOW",
    },
    {
        "name": "Incorrect priority",
        "expected": {"action": "create_task", "priority": "high"},
        "proposed": {"action": "create_task", "priority": "low"},
        "role": "Manager",
        "expected_decision": "BLOCK",
    },
    {
        "name": "Unauthorized action",
        "expected": {"action": "delete_task"},
        "proposed": {"action": "delete_task"},
        "role": "Viewer",
        "expected_decision": "BLOCK",
    },
]


# Run tests
passed = 0

for test in test_cases:
    actual = evaluate_action(test["expected"], test["proposed"], test["role"])

    if actual == test["expected_decision"]:
        status = "PASSED"
        passed += 1
    else:
        status = "FAILED"

    print(test["name"], ":", status)
    print("Expected:", test["expected_decision"])
    print("Actual:", actual)
    print()


# Evaluation summary
total = len(test_cases)
accuracy = (passed / total) * 100

print("===== EVALUATION SUMMARY =====")
print("Tests Passed:", passed)
print("Total Tests:", total)
print("Test Accuracy:", accuracy, "%")
