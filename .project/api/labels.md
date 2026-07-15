# Labels API Reference

Allows configuring and assigning workspace and project scoped categorization tags. Labels can be assigned to both **Tasks** and **Projects**.

---

## List Workspace Labels

Retrieve all active workspace-wide labels.

- **URL**: `/project/<uuid:workspace_id>/labels/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
      "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
      "project": null,
      "name": "Global Bug",
      "slug": "global-bug",
      "color": "#EF4444",
      "description": "Workspace-wide critical issues",
      "position": 0,
      "is_archived": false,
      "created_at": "2026-07-15T12:00:00Z",
      "updated_at": "2026-07-15T12:00:00Z"
    }
  ]
  ```

---

## List All Labels

Retrieve all active labels in the workspace (both workspace-wide and project-scoped).

- **URL**: `/project/<uuid:workspace_id>/labels/all/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
      "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
      "project": null,
      "name": "Global Bug",
      "slug": "global-bug",
      "color": "#EF4444",
      "description": "Workspace-wide critical issues",
      "position": 0,
      "is_archived": false,
      "created_at": "2026-07-15T12:00:00Z",
      "updated_at": "2026-07-15T12:00:00Z"
    },
    {
      "id": "3be58d4a-5f33-4bc7-bd92-38dcf16d41a7",
      "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
      "project": "c88f28fa-678a-4d2b-9804-58a2cd1c7811",
      "name": "Project Special Bug",
      "slug": "project-special-bug",
      "color": "#F59E0B",
      "description": "Project specific category",
      "position": 0,
      "is_archived": false,
      "created_at": "2026-07-15T12:10:00Z",
      "updated_at": "2026-07-15T12:10:00Z"
    }
  ]
  ```

---


## Create Workspace Label

Create a new workspace-wide label.

- **URL**: `/project/<uuid:workspace_id>/labels/`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
  ```json
  {
    "name": "Global Feature",
    "color": "#3B82F6",
    "description": "Workspace-wide feature request"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "77cc49d0-c3d6-444a-a433-28827c12560e",
    "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
    "project": null,
    "name": "Global Feature",
    "slug": "global-feature",
    "color": "#3B82F6",
    "description": "Workspace-wide feature request",
    "position": 1,
    "is_archived": false,
    "created_at": "2026-07-15T12:05:00Z",
    "updated_at": "2026-07-15T12:05:00Z"
  }
  ```

---

## List Project Labels

Retrieve all active labels available for a specific project. This includes both workspace-wide labels AND project-scoped labels.

- **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/labels/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
      "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
      "project": null,
      "name": "Global Bug",
      "slug": "global-bug",
      "color": "#EF4444",
      "description": "Workspace-wide critical issues",
      "position": 0,
      "is_archived": false,
      "created_at": "2026-07-15T12:00:00Z",
      "updated_at": "2026-07-15T12:00:00Z"
    },
    {
      "id": "3be58d4a-5f33-4bc7-bd92-38dcf16d41a7",
      "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
      "project": "c88f28fa-678a-4d2b-9804-58a2cd1c7811",
      "name": "Project Special Bug",
      "slug": "project-special-bug",
      "color": "#F59E0B",
      "description": "Project specific category",
      "position": 0,
      "is_archived": false,
      "created_at": "2026-07-15T12:10:00Z",
      "updated_at": "2026-07-15T12:10:00Z"
    }
  ]
  ```

---

## Create Project Label

Create a new project-scoped label.

- **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/labels/`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
  ```json
  {
    "name": "Project Task",
    "color": "#10B981",
    "description": "Category for LTP task"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "99ee49b0-c3d6-444a-a433-28827c12560e",
    "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
    "project": "c88f28fa-678a-4d2b-9804-58a2cd1c7811",
    "name": "Project Task",
    "slug": "project-task",
    "color": "#10B981",
    "description": "Category for LTP task",
    "position": 1,
    "is_archived": false,
    "created_at": "2026-07-15T12:15:00Z",
    "updated_at": "2026-07-15T12:15:00Z"
  }
  ```

---

## Get Label Detail

Retrieve details of a single label.

- **URL**: `/project/<uuid:workspace_id>/labels/<uuid:label_id>/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK)**:
  ```json
  {
    "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
    "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
    "project": null,
    "name": "Global Bug",
    "slug": "global-bug",
    "color": "#EF4444",
    "description": "Workspace-wide critical issues",
    "position": 0,
    "is_archived": false,
    "created_at": "2026-07-15T12:00:00Z",
    "updated_at": "2026-07-15T12:00:00Z"
  }
  ```

---

## Update Label

Modify fields of a label (e.g. name, color, description).

- **URL**: `/project/<uuid:workspace_id>/labels/<uuid:label_id>/`
- **Method**: `PATCH`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
  ```json
  {
    "name": "Global Serious Bug",
    "color": "#DC2626"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
    "workspace_id": "c71de24f-ef04-4b53-bcfd-f8a42c38520a",
    "project": null,
    "name": "Global Serious Bug",
    "slug": "global-serious-bug",
    "color": "#DC2626",
    "description": "Workspace-wide critical issues",
    "position": 0,
    "is_archived": false,
    "created_at": "2026-07-15T12:00:00Z",
    "updated_at": "2026-07-15T12:20:00Z"
  }
  ```

---

## Delete Label

Archive/soft-delete a label.

- **URL**: `/project/<uuid:workspace_id>/labels/<uuid:label_id>/`
- **Method**: `DELETE`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response (204 No Content)**:
  *(Empty body)*
