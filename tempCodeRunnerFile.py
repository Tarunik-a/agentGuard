actual = ["VALID", "VALID", "INVALID", "INVALID", "VALID"]

predicted = ["ALLOW", "ALLOW", "BLOCK", "ALLOW", "ALLOW"]

valid_total = 0
valid_allowed = 0

invalid_total = 0
invalid_blocked = 0

for i in range(len(actual)):
    if actual[i] == "VALID":
        valid_total += 1

        if predicted[i] == "ALLOW":
            valid_allowed += 1

    elif actual[i] == "INVALID":
        invalid_total += 1

        if predicted[i] == "BLOCK":
            invalid_blocked += 1


acceptance_rate = (valid_allowed / valid_total) * 100

detection_rate = (invalid_blocked / invalid_total) * 100

print("Valid Action Acceptance Rate:", acceptance_rate, "%")
print("Invalid Action Detection Rate:", detection_rate, "%")
