actual = ["VALID", "VALID", "INVALID", "INVALID", "VALID"]

predicted = ["ALLOW", "BLOCK", "BLOCK", "ALLOW", "ALLOW"]

# Initialize counters
TP = 0
TN = 0
FP = 0
FN = 0

valid_total = 0
invalid_total = 0

# Evaluate each test
for i in range(len(actual)):
    if actual[i] == "VALID":
        valid_total += 1

        if predicted[i] == "ALLOW":
            TN += 1
        else:
            FP += 1

    elif actual[i] == "INVALID":
        invalid_total += 1

        if predicted[i] == "BLOCK":
            TP += 1
        else:
            FN += 1


# Calculate metrics
total_tests = len(actual)

correct = TP + TN

accuracy = (correct / total_tests) * 100

acceptance = (TN / valid_total) * 100

detection = (TP / invalid_total) * 100

precision = (TP / (TP + FP)) * 100 if TP + FP else 0

recall = (TP / (TP + FN)) * 100 if TP + FN else 0

f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0


# Generate evaluation report
report = {
    "total_tests": total_tests,
    "true_positives": TP,
    "true_negatives": TN,
    "false_positives": FP,
    "false_negatives": FN,
    "accuracy": round(accuracy, 2),
    "acceptance_rate": round(acceptance, 2),
    "detection_rate": round(detection, 2),
    "precision": round(precision, 2),
    "recall": round(recall, 2),
    "f1_score": round(f1, 2),
}


# Display report
print("\n========== AGENTGUARD EVALUATION REPORT ==========")

for key, value in report.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

print("==================================================")
