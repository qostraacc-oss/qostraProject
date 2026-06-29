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
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
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
* **Access Control**: Creator + `owner`, `admin` roles.
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
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
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
* **Access Control**: Creator + `owner`, `admin` roles.
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
* **Access Control**: Creator + `owner`, `admin` roles.
* **Success Response (204 No Content)**:
  *No response body returned.*


---

## 2. Column CRUD Endpoints

### List Columns
Retrieve all columns for a specific board.

* **URL Route**: `GET /project/<uuid:workspace_id>/boards/<uuid:board_id>/columns/`
* **Method**: `GET`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `board_id`: UUID of the target board.
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
* **Success Response (200 OK)**:
  ```json
  [
    {
      "id": "e0b9687e-405f-4db4-bb1a-f7dc29a149c4",
      "board": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
      "name": "To Do",
      "position": 0,
      "category": "OPEN",
      "color": "#9CA3AF",
      "created_at": "2026-06-29T12:00:00Z",
      "updated_at": "2026-06-29T12:00:00Z"
    }
  ]
  ```

---

### Create Column
Create a new column on a board.

* **URL Route**: `POST /project/<uuid:workspace_id>/boards/<uuid:board_id>/columns/`
* **Method**: `POST`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `board_id`: UUID of the target board.
* **Access Control**: Creator + `owner`, `admin` roles.
* **Request Body**:
  ```json
  {
    "name": "In Progress",
    "position": 1,
    "category": "OPEN",
    "color": "#3B82F6"
  }
  ```
* **Success Response (201 Created)**:
  ```json
  {
    "id": "f5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "board": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "name": "In Progress",
    "position": 1,
    "category": "OPEN",
    "color": "#3B82F6",
    "created_at": "2026-06-29T12:05:00Z",
    "updated_at": "2026-06-29T12:05:00Z"
  }
  ```
* **Error Response (400 Bad Request)**:
  *Occurs if a column with the same name already exists on this board.*
  ```json
  {
    "name": [
      "A column with this name already exists on this board."
    ]
  }
  ```
---

### Reorder Columns
Reorder all columns for a specific board.

* **URL Route**: `PATCH /project/<uuid:workspace_id>/boards/<uuid:board_id>/columns/reorder/`
* **Method**: `PATCH`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `board_id`: UUID of the target board.
* **Access Control**: Creator + `owner`, `admin` roles.
* **Request Body**:
  ```json
  {
    "column_ids": [
      "f5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
      "e0b9687e-405f-4db4-bb1a-f7dc29a149c4"
    ]
  }
  ```
* **Success Response (200 OK)**:
  Returns the complete list of columns sorted by their updated position:
  ```json
  [
    {
      "id": "f5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
      "board": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
      "name": "In Progress",
      "position": 0,
      "category": "OPEN",
      "color": "#3B82F6",
      "created_at": "2026-06-29T12:05:00Z",
      "updated_at": "2026-06-29T12:10:00Z"
    },
    {
      "id": "e0b9687e-405f-4db4-bb1a-f7dc29a149c4",
      "board": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
      "name": "To Do",
      "position": 1,
      "category": "OPEN",
      "color": "#9CA3AF",
      "created_at": "2026-06-29T12:00:00Z",
      "updated_at": "2026-06-29T12:10:00Z"
    }
  ]

  ```

---

### Retrieve Column Details
Fetch the details of a specific column.

* **URL Route**: `GET /project/<uuid:workspace_id>/columns/<uuid:column_id>/`
* **Method**: `GET`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `column_id`: UUID of the target column.
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
* **Success Response (200 OK)**:
  ```json
  {
    "id": "f5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "board": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "name": "In Progress",
    "position": 1,
    "category": "OPEN",
    "color": "#3B82F6",
    "created_at": "2026-06-29T12:05:00Z",
    "updated_at": "2026-06-29T12:05:00Z"
  }
  ```

---

### Update Column
Partially update a column's details (e.g. name, category, or color). Note that the `position` field cannot be modified directly via this endpoint.

* **URL Route**: `PATCH /project/<uuid:workspace_id>/columns/<uuid:column_id>/`
* **Method**: `PATCH`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `column_id`: UUID of the target column.
* **Access Control**: Creator + `owner`, `admin` roles.
* **Request Body**:
  ```json
  {
    "name": "QA testing"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "id": "f5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "board": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "name": "QA testing",
    "position": 1,
    "category": "OPEN",
    "color": "#3B82F6",
    "created_at": "2026-06-29T12:05:00Z",
    "updated_at": "2026-06-29T12:10:00Z"
  }
  ```
* **Error Response (400 Bad Request)**:
  *Occurs if the `position` field is supplied in the patch payload.*
  ```json
  {
    "position": [
      "Position cannot be modified directly. Use the bulk reorder endpoint instead."
    ]
  }
  ```

---

### Delete Column
Delete a specific column.

* **URL Route**: `DELETE /project/<uuid:workspace_id>/columns/<uuid:column_id>/`
* **Method**: `DELETE`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `column_id`: UUID of the target column.
* **Access Control**: Creator + `owner`, `admin` roles.
* **Success Response (204 No Content)**:
  *No response body returned.*


