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


---

## 3. Task CRUD and Reordering Endpoints

### List Tasks
Retrieve tasks for a project.

> [!NOTE]
> **Role-based Visibility**: Project creators, owners, and admins can view all tasks in the project. Standard members and viewers can only view tasks that are explicitly assigned to them.

* **URL Route**: `GET /project/<uuid:workspace_id>/projects/<uuid:project_id>/tasks/`
* **Method**: `GET`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `project_id`: UUID of the target project.
* **Query Parameters**:
  - `column_id` (optional): Filter tasks by column.
  - `assignee_id` (optional): Filter tasks by assignee user.
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
* **Success Response (200 OK)**:
  ```json
  [
    {
      "id": "e98e27c1-9a1b-4cf5-9cd8-7c89f5bc3a2d",
      "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
      "number": 1,
      "type": "TASK",
      "column": "a3b2c1d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "status": "TODO",
      "position": 0,
      "title": "Configure Redis Cache",
      "description": "Set up Redis client and configure cache backends for performance.",
      "priority": "HIGH",
      "estimate": "6.50",
      "time_spent": "0.00",
      "reporter": "7c89f5bc-9cd8-4cf5-9a1b-e98e27c123fa",
      "assignee": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
      "watchers": [
        "d748f219-c09a-4c9f-8561-12503ea29ad3"
      ],
      "start_date": "2026-07-01",
      "due_date": "2026-07-05",
      "completed_at": null,
      "is_archived": false,
      "created_at": "2026-06-30T13:59:00Z",
      "updated_at": "2026-06-30T13:59:00Z"
    }
  ]
  ```

---

### Create Task
Create a new task inside a project.

* **URL Route**: `POST /project/<uuid:workspace_id>/projects/<uuid:project_id>/tasks/`
* **Method**: `POST`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `project_id`: UUID of the target project.
* **Access Control**: Creator + `owner`, `admin`, `member` roles.
* **Request Body**:
  ```json
  {
    "title": "Configure Redis Cache",
    "description": "Set up Redis client and configure cache backends for performance.",
    "type": "TASK",
    "column": "a3b2c1d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "priority": "HIGH",
    "estimate": "6.50",
    "assignee": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "start_date": "2026-07-01",
    "due_date": "2026-07-05",
    "watchers": [
      "d748f219-c09a-4c9f-8561-12503ea29ad3"
    ]
  }
  ```
* **Success Response (201 Created)**:
  ```json
  {
    "id": "e98e27c1-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "number": 1,
    "type": "TASK",
    "column": "a3b2c1d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "status": "TODO",
    "position": 0,
    "title": "Configure Redis Cache",
    "description": "Set up Redis client and configure cache backends for performance.",
    "priority": "HIGH",
    "estimate": "6.50",
    "time_spent": "0.00",
    "reporter": "7c89f5bc-9cd8-4cf5-9a1b-e98e27c123fa",
    "assignee": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "watchers": [
      "d748f219-c09a-4c9f-8561-12503ea29ad3"
    ],
    "start_date": "2026-07-01",
    "due_date": "2026-07-05",
    "completed_at": null,
    "is_archived": false,
    "created_at": "2026-06-30T13:59:00Z",
    "updated_at": "2026-06-30T13:59:00Z"
  }
  ```

---

### Retrieve Task Details
Fetch the details of a specific task.

* **URL Route**: `GET /project/<uuid:workspace_id>/tasks/<uuid:task_id>/`
* **Method**: `GET`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `task_id`: UUID of the target task.
* **Access Control**: Creator + `owner`, `admin`. Standard `member` and `viewer` can only access if they are the task's assignee.
* **Success Response (200 OK)**:
  ```json
  {
    "id": "e98e27c1-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "number": 1,
    "type": "TASK",
    "column": "a3b2c1d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "status": "TODO",
    "position": 0,
    "title": "Configure Redis Cache",
    "description": "Set up Redis client and configure cache backends for performance.",
    "priority": "HIGH",
    "estimate": "6.50",
    "time_spent": "0.00",
    "reporter": "7c89f5bc-9cd8-4cf5-9a1b-e98e27c123fa",
    "assignee": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "watchers": [
      "d748f219-c09a-4c9f-8561-12503ea29ad3"
    ],
    "start_date": "2026-07-01",
    "due_date": "2026-07-05",
    "completed_at": null,
    "is_archived": false,
    "created_at": "2026-06-30T13:59:00Z",
    "updated_at": "2026-06-30T13:59:00Z"
  }
  ```

---

### Update Task
Partially update a task's details. Direct updates to `position` or `column` are blocked.

* **URL Route**: `PATCH /project/<uuid:workspace_id>/tasks/<uuid:task_id>/`
* **Method**: `PATCH`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `task_id`: UUID of the target task.
* **Access Control**: Creator + `owner`, `admin`. Standard `member` can only update if they are the task's assignee.
* **Request Body**:
  ```json
  {
    "title": "Configure Redis Cache (Updated)",
    "estimate": "8.00"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "id": "e98e27c1-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "number": 1,
    "type": "TASK",
    "column": "a3b2c1d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "status": "TODO",
    "position": 0,
    "title": "Configure Redis Cache (Updated)",
    "description": "Set up Redis client and configure cache backends for performance.",
    "priority": "HIGH",
    "estimate": "8.00",
    "time_spent": "0.00",
    "reporter": "7c89f5bc-9cd8-4cf5-9a1b-e98e27c123fa",
    "assignee": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "watchers": [
      "d748f219-c09a-4c9f-8561-12503ea29ad3"
    ],
    "start_date": "2026-07-01",
    "due_date": "2026-07-05",
    "completed_at": null,
    "is_archived": false,
    "created_at": "2026-06-30T13:59:00Z",
    "updated_at": "2026-06-30T14:15:00Z"
  }
  ```
* **Error Response (400 Bad Request)**:
  *Occurs if the `position` or `column` field is supplied in the patch payload.*
  ```json
  {
    "position": [
      "Position cannot be modified directly. Use the move endpoint instead."
    ]
  }
  ```

---

### Move / Reorder Task
Move a task within a column, or shift it to a different column.

* **URL Route**: `PATCH /project/<uuid:workspace_id>/tasks/<uuid:task_id>/move/`
* **Method**: `PATCH`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `task_id`: UUID of the target task.
* **Access Control**: Creator + `owner`, `admin`. Standard `member` can only move if they are the task's assignee.
* **Request Body**:
  ```json
  {
    "target_column_id": "b5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "target_position": 1
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "id": "e98e27c1-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "project": "23fa3210-449e-4c54-8c88-e216dbdebc9a",
    "number": 1,
    "type": "TASK",
    "column": "b5127d89-9a1b-4cf5-9cd8-7c89f5bc3a2d",
    "status": "TODO",
    "position": 1,
    "title": "Configure Redis Cache (Updated)",
    "description": "Set up Redis client and configure cache backends for performance.",
    "priority": "HIGH",
    "estimate": "8.00",
    "time_spent": "0.00",
    "reporter": "7c89f5bc-9cd8-4cf5-9a1b-e98e27c123fa",
    "assignee": "402c918a-9e12-4eb8-a1bf-54cb37f61c6b",
    "watchers": [
      "d748f219-c09a-4c9f-8561-12503ea29ad3"
    ],
    "start_date": "2026-07-01",
    "due_date": "2026-07-05",
    "completed_at": null,
    "is_archived": false,
    "created_at": "2026-06-30T13:59:00Z",
    "updated_at": "2026-06-30T14:20:00Z"
  }
  ```

---

### Delete Task
Delete a specific task.

* **URL Route**: `DELETE /project/<uuid:workspace_id>/tasks/<uuid:task_id>/`
* **Method**: `DELETE`
* **URL Params**:
  - `workspace_id`: UUID of the active workspace.
  - `task_id`: UUID of the target task.
* **Access Control**: Creator + `owner`, `admin`. Standard `member` can only delete if they are the task's assignee.
* **Success Response (204 No Content)**:
  *No response body returned.*



