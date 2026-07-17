# Execution Assignment & Starting Workflow

## Overview

This document describes the new workflow for assigning executions to users and allowing them to start those executions after they've been created.

## Workflow Steps

### 1. Create Executions (Matrix)

First, create a batch of executions for a test suite across multiple devices:

```bash
POST /api/v1/executions/matrix
Content-Type: application/json

{
  "test_suite_id": 1,
  "run_id": 1,
  "device_ids": [1, 2, 3]
}
```

**Response Example:**
```json
[
  {
    "id": 1,
    "device_id": 1,
    "run_id": 1,
    "test_case_version_id": 10,
    "status_id": null,
    "attachment_id": null,
    "resolution_id": null,
    "actual_result": null,
    "execution_order": 1,
    "assigned_to": null,
    "executed_by": null,
    "updated_by": null,
    "started_at": null,
    "executed_at": null,
    "updated_at": null
  },
  {
    "id": 2,
    "device_id": 1,
    "run_id": 1,
    "test_case_version_id": 11,
    "status_id": null,
    "attachment_id": null,
    "resolution_id": null,
    "actual_result": null,
    "execution_order": 2,
    "assigned_to": null,
    "executed_by": null,
    "updated_by": null,
    "started_at": null,
    "executed_at": null,
    "updated_at": null
  }
]
```

Note: All executions start with `assigned_to: null` and `started_at: null`.

---

### 2. Assign Executions to Users

#### Option A: Assign Single Execution

Assign one execution to a specific user (admin only):

```bash
POST /api/v1/executions/{execution_id}/assign
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_id": 5
}
```

**Response:**
```json
{
  "id": 1,
  "device_id": 1,
  "run_id": 1,
  "test_case_version_id": 10,
  "status_id": null,
  "attachment_id": null,
  "resolution_id": null,
  "actual_result": null,
  "execution_order": 1,
  "assigned_to": 5,
  "executed_by": null,
  "updated_by": null,
  "started_at": null,
  "executed_at": null,
  "updated_at": null
}
```

#### Option B: Bulk Assign Multiple Executions

Assign multiple executions to a single user in one request (admin only):

```bash
POST /api/v1/executions/bulk/assign
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "execution_ids": [1, 2, 3],
  "user_id": 5
}
```

**Response:**
```json
[
  {
    "id": 1,
    "device_id": 1,
    "run_id": 1,
    "test_case_version_id": 10,
    "status_id": null,
    "attachment_id": null,
    "resolution_id": null,
    "actual_result": null,
    "execution_order": 1,
    "assigned_to": 5,
    "executed_by": null,
    "updated_by": null,
    "started_at": null,
    "executed_at": null,
    "updated_at": null
  },
  {
    "id": 2,
    "device_id": 1,
    "run_id": 1,
    "test_case_version_id": 11,
    "status_id": null,
    "attachment_id": null,
    "resolution_id": null,
    "actual_result": null,
    "execution_order": 2,
    "assigned_to": 5,
    "executed_by": null,
    "updated_by": null,
    "started_at": null,
    "executed_at": null,
    "updated_at": null
  },
  {
    "id": 3,
    "device_id": 2,
    "run_id": 1,
    "test_case_version_id": 12,
    "status_id": null,
    "attachment_id": null,
    "resolution_id": null,
    "actual_result": null,
    "execution_order": 3,
    "assigned_to": 5,
    "executed_by": null,
    "updated_by": null,
    "started_at": null,
    "executed_at": null,
    "updated_at": null
  }
]
```

---

### 3. Start an Execution

The assigned user (or an admin) can now start an execution, which sets the `started_at` timestamp:

```bash
POST /api/v1/executions/{execution_id}/start
Authorization: Bearer {user_token}
Content-Type: application/json

{}
```

**Response:**
```json
{
  "id": 1,
  "device_id": 1,
  "run_id": 1,
  "test_case_version_id": 10,
  "status_id": null,
  "attachment_id": null,
  "resolution_id": null,
  "actual_result": null,
  "execution_order": 1,
  "assigned_to": 5,
  "executed_by": null,
  "updated_by": null,
  "started_at": "2026-07-13T10:30:45.123456+00:00",
  "executed_at": null,
  "updated_at": null
}
```

---

## Permission Model

| Operation | Required Role | Notes |
|-----------|--------------|-------|
| Create Executions | Authenticated User | Via `/executions/matrix` endpoint |
| Assign Single Execution | Admin | Only admin can assign |
| Assign Bulk Executions | Admin | Only admin can assign |
| Start Execution | Assigned User OR Admin | Assigned user can start their own; admins can start any |
| Update Execution | Authenticated User | Can update status, attachment, resolution, etc. |
| Delete Execution | Admin | Only admin can delete |

---

## Execution States

An execution flows through these states:

### Initial State (After Creation)
```json
{
  "assigned_to": null,
  "started_at": null,
  "executed_by": null,
  "executed_at": null,
  "status_id": null
}
```

### After Assignment
```json
{
  "assigned_to": 5,
  "started_at": null,
  "executed_by": null,
  "executed_at": null,
  "status_id": null
}
```

### After Starting
```json
{
  "assigned_to": 5,
  "started_at": "2026-07-13T10:30:45.123456+00:00",
  "executed_by": null,
  "executed_at": null,
  "status_id": null
}
```

### After Updating with Status
```json
{
  "assigned_to": 5,
  "started_at": "2026-07-13T10:30:45.123456+00:00",
  "executed_by": 5,
  "executed_at": "2026-07-13T10:35:20.789123+00:00",
  "status_id": 2
}
```

---

## API Endpoints Summary

### New Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/executions/{execution_id}/assign` | Assign single execution to user | Admin |
| POST | `/executions/bulk/assign` | Assign multiple executions to user | Admin |
| POST | `/executions/{execution_id}/start` | Start an execution | Assigned User OR Admin |

### Related Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/executions/matrix` | Create executions | Authenticated |
| GET | `/executions/{execution_id}` | Get execution details | Authenticated |
| GET | `/executions/run/{run_id}` | List executions by run | Authenticated |
| PATCH | `/executions/{execution_id}` | Update execution (status, etc.) | Authenticated |
| DELETE | `/executions/{execution_id}` | Delete execution | Admin |

---

## Error Handling

### Assignment Errors

- **User not found**: Returns 400 with message "User not found"
- **Execution not found**: Returns 400 with message "Execution not found"
- **One or more executions not found** (bulk): Returns 400 with message "One or more executions were not found"

### Start Errors

- **Execution not found**: Returns 400 with message "Execution not found"
- **Already started**: Returns 400 with message "Execution has already been started"
- **Not assigned to user**: Returns 400 with message "Only the assigned user can start this execution"

### Example Error Response
```json
{
  "detail": "User not found"
}
```

---

## Database Schema

The `executions` table includes these relevant columns:

```sql
assigned_to INTEGER FOREIGN KEY(users.id) -- User assigned to execute
started_at TIMESTAMP WITH TIMEZONE -- When execution was started
executed_by INTEGER FOREIGN KEY(users.id) -- User who executed/completed
executed_at TIMESTAMP WITH TIMEZONE -- When execution was completed
status_id INTEGER FOREIGN KEY(statuses.id) -- Final status
```

### Indexes for Performance
- `execution_assignee_idx` on `assigned_to`
- `execution_executor_idx` on `executed_by`

---

## Complete Workflow Example

```bash
# 1. Admin creates executions for a test run
curl -X POST http://localhost:8000/api/v1/executions/matrix \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "test_suite_id": 1,
    "run_id": 1,
    "device_ids": [1, 2, 3]
  }'

# Response shows 3 executions with assigned_to: null

# 2. Admin assigns 3 executions to user 5
curl -X POST http://localhost:8000/api/v1/executions/bulk/assign \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "execution_ids": [1, 2, 3],
    "user_id": 5
  }'

# Response shows all 3 executions with assigned_to: 5

# 3. User 5 starts executing (sets started_at)
curl -X POST http://localhost:8000/api/v1/executions/1/start \
  -H "Authorization: Bearer $USER_5_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Response shows execution 1 with started_at: "2026-07-13T10:30:45.123456+00:00"

# 4. User 5 updates execution with status and results
curl -X PATCH http://localhost:8000/api/v1/executions/1 \
  -H "Authorization: Bearer $USER_5_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status_id": 2,
    "actual_result": "Test passed successfully"
  }'

# Response shows execution with executed_by: 5, executed_at: "...", status_id: 2
```

---

## Notes

- **started_at** is different from **executed_at**: 
  - `started_at` marks when the user began work
  - `executed_at` is set when they submit a status (test completion)

- **Assignment is optional**: An execution without an assignee can still be updated by any authenticated user, but the `/start` endpoint will reject it with an authorization error

- **Bulk operations**: Use bulk assign when distributing many executions at once to improve API efficiency

- **Idempotency**: The `/start` endpoint cannot be called twice on the same execution (returns error if already started)
