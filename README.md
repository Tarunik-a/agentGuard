# AgentGuard
### AI Agent Reliability and Verification Framework

AgentGuard is a reliability and verification framework designed to make AI agent tool execution safer, more controlled, and more trustworthy.

It evaluates proposed actions before execution using schema validation, intent verification, permission checks, and risk assessment. After execution, it verifies the resulting state, detects failures, and records supporting evidence in structured audit reports.

---

## Problem Statement

AI agents interact with external tools and systems to perform tasks. However, they may:

- Propose actions that do not match user intent.
- Attempt operations without sufficient permissions.
- Select invalid parameters or action formats.
- Execute operations incorrectly.
- Report success even when the intended outcome was not achieved.

AgentGuard addresses these reliability challenges through pre-execution validation, controlled execution, and post-execution verification.

## Key Features

- **Schema Validation:** Validates proposed actions against predefined action schemas.
- **Intent Verification:** Checks whether the proposed action matches the expected user intent.
- **Role-Based Access Control:** Restricts actions according to user permissions.
- **Risk Assessment:** Classifies actions based on their risk level.
- **Execution Control:** Allows, blocks, or requests human approval for proposed actions.
- **State Verification:** Checks whether the actual execution result matches the expected outcome.
- **Failure Detection:** Identifies unsuccessful executions and incorrect results.
- **Evidence Collection:** Records verification evidence to support execution decisions.
- **Audit Logging:** Stores structured execution reports in JSONL format.
- **Automated Testing:** Uses Pytest to test validation, execution, verification, and audit functionality.

## Architecture

AgentGuard follows a multi-stage execution and verification workflow.

```text
        Proposed Agent Action
                 |
                 v
         Schema Validation
                 |
                 v
         Intent Verification
                 |
                 v
        Permission Validation
                 |
                 v
          Risk Assessment
                 |
                 v
         Execution Decision
                 |
       +---------+---------+
       |         |         |
       v         v         v
     ALLOW     BLOCK    HUMAN REVIEW
       |                   |
       |              Approval?
       |              /       \
       |            Yes        No
       |             |          |
       +-------------+          |
                 |              |
                 v              v
          Action Execution   Not Executed
                 |
                 v
         State Verification
                 |
                 v
         Evidence Collection
                 |
                 v
          Outcome Analysis
                 |
                 v
           Audit Logging
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core framework development |
| Pydantic | Action schema validation |
| Pytest | Automated testing |
| JSON / JSONL | Structured audit records |
| Git and GitHub | Version control |

Additional technologies such as FastAPI, MySQL, SQLAlchemy, React, and Docker are planned for future development.

## Project Structure

```text
AgentGuard/
│
├── agentguard.py
├── metrics.py
├── audit_log.jsonl
├── README.md
│
└── tests/
    └── test_agentguard.py
```

## Current Implementation

The current implementation supports three simulated task operations:

| Action | Description |
|---|---|
| create_task | Creates a task |
| view_task | Retrieves an existing task |
| delete_task | Deletes an existing task |

### Role-Based Permissions

| Role | Create Task | View Task | Delete Task |
|---|---|---|---|
| Admin | Yes | No | Yes |
| Manager | Yes | No | No |
| Viewer | No | Yes | No |

### Risk Classification

| Action | Risk Level |
|---|---|
| create_task | Medium |
| view_task | Low |
| delete_task | High |

High-risk actions require human approval before execution.

## Execution and Verification

AgentGuard separates action execution from outcome verification.

1. A proposed action is validated.
2. Its intent and permissions are checked.
3. Its risk level determines the execution decision.
4. Approved actions are executed.
5. The resulting state is checked against the expected outcome.
6. Verification evidence and diagnostic messages are collected.
7. The final outcome is stored in an audit record.

This approach helps detect cases where an operation reports success but the intended state change did not actually occur.

## Audit Logging

AgentGuard generates structured audit records containing information such as:

- Record ID
- Schema validation status
- Intent validation status
- Permission status
- Risk level
- Execution decision
- Execution status
- Verification status
- Final outcome
- Errors and diagnostic messages
- Verification evidence

Audit records are stored in JSON Lines (`.jsonl`) format.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AgentGuard.git
```

### 2. Navigate to the project directory

```bash
cd AgentGuard
```

### 3. Install dependencies

```bash
pip install pydantic pytest ollama sqlalchemy pymysql python-dotenv
```

### 4.Database Configuration

### 1. Install and start MySQL

### 2. Create the database

CREATE DATABASE agentguard_db;

### 3. Create a .env file

Create it in the AgentGuard project root.

### 4. Configure database credentials

DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=agentguard_db
### 5. Run AgentGuard

```bash
python agentguard.py
```

## Running Tests

Run the complete automated test suite:

```bash
python -m pytest tests/test_agentguard.py -v
```

The tests cover:

- Schema validation
- Intent verification
- Permission checking
- Risk classification
- Execution decisions
- Task operations
- Human approval
- State verification
- False-success detection
- Verification evidence
- Audit record persistence
- Failure diagnostics

## Current Limitations

- Task operations currently use simulated in-memory storage.
- The verification store is an in-memory implementation, not an independent database.
- Integration with an actual AI agent is not yet implemented.
- The current system supports a limited set of task operations.
- A graphical monitoring dashboard is not yet available.


## Project Objective

The long-term objective of AgentGuard is to provide a reusable reliability layer that can evaluate AI agent actions before execution and independently verify their outcomes afterward.

The framework aims to improve the trustworthiness, accountability, and reliability of AI agents interacting with external tools.

---

**Project:** AgentGuard  
**Category:** AI / Machine Learning / Software Engineering  
**Language:** Python
**Status:** Under Development