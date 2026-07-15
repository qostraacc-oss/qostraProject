# TimeLogs API Reference

This document provides details about the endpoints, request/response models, and error responses for the Time Tracking & Time Logs feature.

---

## Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/project/<workspace_id>/tasks/<task_id>/timelogs/` | List all time logs for a specific task |
| `POST` | `/api/project/<workspace_id>/tasks/<task_id>/timelogs/` | Log time spent on a task |
| `GET` | `/api/project/<workspace_id>/timelogs/<id>/` | Retrieve details of a specific time log |
| `PATCH` | `/api/project/<workspace_id>/timelogs/<id>/` | Update a specific time log |
| `DELETE` | `/api/project/<workspace_id>/timelogs/<id>/` | Delete a specific time log |

---

## Details

### 1. List Task Time Logs
* **Route:** `/api/project/<workspace_id>/tasks/<task_id>/timelogs/`
* **Method:** `GET`
* **Headers:**
  * `Authorization: Bearer <access_token>`
* **Response (Success 200 OK):**
  ```json
  [
    {
      "id": "78ec05cc-24ec-4d34-8486-e9bb716e5bfa",
      "task": "33ec05cc-24ec-4d34-8486-e9bb716e5bfb",
      "user": "1ea795e3-915c-45b7-8c7f-1365df199d30",
      "username": "alice",
      "duration": "2.50",
      "description": "Implemented DB models.",
      "logged_at": "2026-07-15",
      "is_locked": false,
      "created_at": "2026-07-15T10:45:00.000Z",
      "updated_at": "2026-07-15T10:45:00.000Z"
    }
  ]
  ```

---

### 2. Log Time
* **Route:** `/api/project/<workspace_id>/tasks/<task_id>/timelogs/`
* **Method:** `POST`
* **Headers:**
  * `Authorization: Bearer <access_token>`
  * `Content-Type: application/json`
* **Request Payload Schema:**
  ```json
  {
    "duration": "3.50",
    "description": "Reviewed PR and refactored authentication module.",
    "logged_at": "2026-07-15"
  }
  ```
* **Response (Success 201 Created):**
  ```json
  {
    "id": "a1ec05cc-24ec-4d34-8486-e9bb716e5bfc",
    "task": "33ec05cc-24ec-4d34-8486-e9bb716e5bfb",
    "user": "1ea795e3-915c-45b7-8c7f-1365df199d30",
    "username": "alice",
    "duration": "3.50",
    "description": "Reviewed PR and refactored authentication module.",
    "logged_at": "2026-07-15",
    "is_locked": false,
    "created_at": "2026-07-15T11:20:00.000Z",
    "updated_at": "2026-07-15T11:20:00.000Z"
  }
  ```
* **Error Response (400 Bad Request - Negative/Zero duration):**
  ```json
  {
    "duration": [
      "Duration must be a positive number."
    ]
  }
  ```

---

### 3. Update Time Log
* **Route:** `/api/project/<workspace_id>/timelogs/<id>/`
* **Method:** `PATCH` / `PUT`
* **Headers:**
  * `Authorization: Bearer <access_token>`
  * `Content-Type: application/json`
* **Request Payload Schema:**
  ```json
  {
    "duration": "4.00"
  }
  ```
* **Response (Success 200 OK):**
  ```json
  {
    "id": "a1ec05cc-24ec-4d34-8486-e9bb716e5bfc",
    "task": "33ec05cc-24ec-4d34-8486-e9bb716e5bfb",
    "user": "1ea795e3-915c-45b7-8c7f-1365df199d30",
    "username": "alice",
    "duration": "4.00",
    "description": "Reviewed PR and refactored authentication module.",
    "logged_at": "2026-07-15",
    "is_locked": false,
    "created_at": "2026-07-15T11:20:00.000Z",
    "updated_at": "2026-07-15T11:25:00.000Z"
  }
  ```
* **Error Response (400 Bad Request - Locked log):**
  ```json
  {
    "non_field_errors": [
      "This time log is locked and cannot be modified."
    ]
  }
  ```

---

### 4. Delete Time Log
* **Route:** `/api/project/<workspace_id>/timelogs/<id>/`
* **Method:** `DELETE`
* **Headers:**
  * `Authorization: Bearer <access_token>`
* **Response (Success 24 No Content)**
* **Error Response (400 Bad Request - Locked log):**
  ```json
  {
    "non_field_errors": [
      "This time log is locked and cannot be deleted."
    ]
  }
  ```
