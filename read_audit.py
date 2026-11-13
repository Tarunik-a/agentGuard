import json

# Read saved audit records
with open("audit_log.jsonl", "r") as file:
    for line in file:
        record = json.loads(line)

        print("\n--- AUDIT RECORD ---")

        print("Timestamp:", record["timestamp"])
        print("Intent:", record["intent"])
        print("Permission:", record["permission"])
        print("Risk:", record["risk"])
        print("Decision:", record["decision"])
        print("Execution:", record["execution"])
        print("Verification:", record["verification"])
        print("Errors:", record["errors"])
