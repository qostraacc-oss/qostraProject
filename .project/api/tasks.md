# Tasks API Reference

This document outlines the API endpoints, request payloads, headers, and response schemas for the Tasks application.

---

## Base Headers
All requests must include the JWT authorization header:
```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## 1. Board CRUD Endpoints

### List Boards
Retrieve all Kanban boards for a specific project in a workspace.

* **URL Route**: `GET /project/<uuid:workspace_id>/<uuid:project_id>/boards/`
* **Method**: `GET`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `project_id`: UUID of the target project.
* **Success Response (200 OK)**:
  ```json
  [
    {
      "id": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
      "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
      "name": "Sprint 1 Board",
      "description": "Main backlog and sprint board",
      "created_at": "2026-06-24T12:00:00Z",
      "updated_at": "2026-06-24T12:00:00Z"
    }
  ]
  ```

---

### Create Board
Create a new Kanban board inside a project.

* **URL Route**: `POST /project/<uuid:workspace_id>/<uuid:project_id>/boards/`
* **Method**: `POST`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `project_id`: UUID of the target project.
* **Request Body**:
  ```json
  {
    "name": "Sprint 2 Board",
    "description": "Board for upcoming sprint"
  }
  ```
* **Success Response (201 Created)**:
  ```json
  {
    "id": "bc1427c3-305f-4d92-bbff-9411624c96a7",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "name": "Sprint 2 Board",
    "description": "Board for upcoming sprint",
    "created_at": "2026-06-24T12:05:00Z",
    "updated_at": "2026-06-24T12:05:00Z"
  }
  ```
* **Error Response (400 Bad Request)**:
  *Occurs if a board with the same name already exists in this project.*
  ```json
  {
    "name": [
      "A board with this name already exists in the project."
    ]
  }
  ```

---

### Retrieve Board Details
Fetch the details of a specific board.

* **URL Route**: `GET /project/<uuid:workspace_id>/boards/<uuid:board_id>/`
* **Method**: `GET`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `board_id`: UUID of the target board.
* **Success Response (200 OK)**:
  ```json
  {
    "id": "bc1427c3-305f-4d92-bbff-9411624c96a7",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "name": "Sprint 2 Board",
    "description": "Board for upcoming sprint",
    "created_at": "2026-06-24T12:05:00Z",
    "updated_at": "2026-06-24T12:05:00Z"
  }
  ```

---

### Update Board
Partially update a board's details (e.g. name or description).

* **URL Route**: `PATCH /project/<uuid:workspace_id>/boards/<uuid:board_id>/`
* **Method**: `PATCH`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `board_id`: UUID of the target board.
* **Request Body**:
  ```json
  {
    "name": "Sprint 2 Board (Updated)",
    "description": "Updated sprint 2 description details"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "id": "bc1427c3-305f-4d92-bbff-9411624c96a7",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "name": "Sprint 2 Board (Updated)",
    "description": "Updated sprint 2 description details",
    "created_at": "2026-06-24T12:05:00Z",
    "updated_at": "2026-06-24T12:10:00Z"
  }
  ```

---

### Delete Board
Delete a specific board.

* **URL Route**: `DELETE /project/<uuid:workspace_id>/boards/<uuid:board_id>/`
* **Method**: `DELETE`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `board_id`: UUID of the target board.
* **Success Response (204 No Content)**:
  *No response body returned.*
