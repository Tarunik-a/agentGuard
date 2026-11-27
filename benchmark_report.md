# AgentGuard – Reliability Benchmark Report

## 1. Project Overview

AgentGuard is an AI agent reliability and verification framework designed to prevent invalid, unauthorized, and incorrectly executed actions.

It acts as an independent control layer between an AI agent and its execution environment.

### Benchmark Objectives

The benchmark evaluates whether AgentGuard can:

- Reject invalid AI-generated actions.
- Prevent unauthorized operations.
- Identify incorrect action parameters.
- Detect execution failures.
- Independently verify task state against database records.
- Preserve evidence of verification results.
- Measure policy evaluation and execution latency.

### Experimental Approach

Two approaches are evaluated:

1. **Baseline:** AI-proposed actions are accepted without AgentGuard policy checks.
2. **AgentGuard:** Proposed actions pass through schema validation, intent checks, permission checks, risk assessment, execution controls, and post-execution verification.

The benchmark uses manually designed scenarios and a local MySQL database.

## 2. Policy Evaluation Results

AgentGuard was evaluated using 20 manually designed scenarios covering valid actions, invalid parameters, missing fields, unsupported actions, and permission violations.

### Results

| Metric | Result |
|---|---:|
| Total scenarios | 20 |
| Correct decisions | 20 |
| Policy accuracy | 100% |
| Valid proposal acceptance rate | 100% |
| Invalid proposal prevention rate | 100% |
| False rejection rate | 0% |

### Baseline Comparison

The baseline accepts every proposed action without applying validation or permission checks.

| Metric | Baseline | AgentGuard |
|---|---:|---:|
| Proposal acceptance rate | 100% | 15% |
| Invalid proposal acceptance rate | 100% | 0% |
| Invalid proposal prevention rate | 0% | 100% |

### Interpretation

The baseline accepted all 20 proposals, including invalid and unauthorized proposals.

AgentGuard correctly classified all 20 manually designed scenarios according to their expected decisions.

These results demonstrate the value of deterministic validation and permission enforcement within the tested scenarios.

## 3. Execution and Verification Results

AgentGuard was evaluated against seven execution-related scenarios.

### Scenario Results

| Scenario | Expected Result | Status |
|---|---|---|
| Valid task creation | Successful execution and verification | PASSED |
| Missing database record | Verification failure detected | PASSED |
| Database execution failure | Execution failure detected | PASSED |
| Incorrect stored task data | Data mismatch detected | PASSED |
| Unauthorized task execution | Execution prevented | PASSED |
| Valid task viewing | Task retrieval verified | PASSED |
| Valid task deletion | Task deletion verified | PASSED |

### Verification Evidence

AgentGuard uses separate database lookup operations to verify the actual state after task execution.

For task creation, it checks whether the stored task exists and whether its title and priority match the expected values.

For task viewing, it checks whether the retrieved task matches the stored database record.

For task deletion, it confirms that the deleted task no longer exists in the database.

### Result

All seven execution-related benchmark scenarios produced their expected outcomes.

AgentGuard also retains structured evidence and diagnostic messages to support verification and failure analysis.

## 4. Performance Evaluation

AgentGuard performance was measured separately for policy evaluation and database-backed execution with verification.

### Policy Evaluation Latency

The policy evaluation benchmark repeatedly measured the time taken by `evaluate_action()`.

The observed average policy evaluation latency was approximately **0.002571 ms per scenario** in the recorded run.

### Execution and Verification Latency

The execution benchmark measured database-backed task viewing and post-execution verification over 20 iterations.

| Metric | Result |
|---|---:|
| Iterations | 20 |
| Successful iterations | 20 |
| Failed iterations | 0 |
| Average latency | 11.7339 ms |

Task creation and cleanup were excluded from the measured execution and verification interval.

### Performance Interpretation

Policy evaluation and database-backed execution have different workloads. Policy evaluation performs deterministic checks, whereas execution and verification involve database operations.

The latency measurements are specific to the local development environment and should not be treated as universal performance guarantees.

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core framework |
| Pydantic | Structured action validation |
| Pytest | Automated testing |
| Ollama | Local AI model integration |
| Qwen 2.5 3B | Local action proposal generation |
| MySQL | Persistent task and audit storage |
| SQLAlchemy | Database interaction |
| Python-dotenv | Environment configuration |

## 6. Limitations

The current benchmark has several limitations:

1. The evaluation dataset contains manually designed scenarios rather than a large, independently collected dataset.
2. Intent verification uses deterministic keyword and parameter matching. It is not a complete semantic understanding system.
3. Baseline behavior is a simple always-ALLOW implementation, not a comparison against another advanced agent framework.
4. Baseline latency and AgentGuard policy latency are not directly equivalent because they perform different amounts of work.
5. Execution and verification use the same MySQL database, although verification performs a separate database lookup.
6. The latency results are based on a small number of iterations on one local machine.
7. The benchmark does not yet evaluate concurrent workloads, large datasets, or distributed environments.

## 7. Future Improvements

Future development can include:

- Larger and more diverse benchmark datasets.
- More sophisticated natural-language intent verification.
- Independent verification through a separate storage or monitoring system.
- Concurrent execution and stress testing.
- More detailed latency measurements, including percentiles.
- Comparison with additional baseline agent implementations.
- API integration using FastAPI.
- A React dashboard for audit reports and benchmark metrics.
- Continuous integration and automated benchmark execution.

## 8. Conclusion

The AgentGuard benchmark demonstrates that a deterministic reliability layer can improve the handling of AI-proposed actions in the tested task-management environment.

In the manually designed policy evaluation scenarios, AgentGuard achieved 100% decision accuracy, prevented all tested invalid proposals, and produced no false rejections.

Execution benchmarks also demonstrated successful task creation, viewing, deletion, failure detection, data mismatch detection, and unauthorized execution prevention.

The results support the value of combining schema validation, permission enforcement, risk assessment, controlled execution, database-backed verification, and evidence-linked auditing.

Further testing with larger datasets, independent verification systems, and more realistic workloads is required before making production-level reliability claims.

---

**Report Status:** Initial benchmark evaluation completed.

**Project:** AgentGuard – AI Agent Reliability and Verification Framework