# Sprints API Reference

This application exposes endpoints for project-specific sprint roadmaps, task associations, and iteration scheduling.

---

## Base Path
All endpoints are prefixed with the workspace scope:
`/project/<uuid:workspace_id>/`

## Sprints Endpoints

### 1. List Sprints
* **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/sprints/`
* **Method**: `GET`
* **Headers**: 
  * `Authorization: Bearer <token>`
* **Query Parameters**:
  * `status=<string>`: (Optional) Filter sprints by status: `PLANNED`, `ACTIVE`, `COMPLETED`.
* **Access Control**: Requires workspace membership and active project access.
* **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "project": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "name": "Sprint 1: Auth & Layout",
      "goal": "Build authentication UI and main layouts.",
      "status": "PLANNED",
      "start_date": "2026-07-20",
      "end_date": "2026-08-03",
      "created_at": "2026-07-15T12:00:00Z",
      "updated_at": "2026-07-15T12:00:00Z"
    }
  ]
  ```

### 2. Create Sprint
* **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/sprints/`
* **Method**: `POST`
* **Headers**:
  * `Authorization: Bearer <token>`
  * `Content-Type: application/json`
* **Request Payload**:
  ```json
  {
    "name": "Sprint 1: Auth & Layout",
    "goal": "Build authentication UI and main layouts.",
    "start_date": "2026-07-20",
    "end_date": "2026-08-03",
    "status": "PLANNED" // optional
  }
  ```
* **Validation Rules**:
  * **Name Uniqueness**: Sprint name must be unique within the project.
  * **Dates Consistency**: `end_date` must be after `start_date`.
* **Success Response**: `201 Created`
  * Returns the newly created Sprint JSON object.

### 3. Retrieve Sprint Detail
* **URL**: `/project/<uuid:workspace_id>/sprints/<uuid:sprint_id>/`
* **Method**: `GET`
* **Headers**:
  * `Authorization: Bearer <token>`
* **Access Control**: Requester must have active project access in the workspace.
* **Success Response**: `200 OK`

### 4. Update Sprint (Partial)
* **URL**: `/project/<uuid:workspace_id>/sprints/<uuid:sprint_id>/`
* **Method**: `PATCH`
* **Headers**:
  * `Authorization: Bearer <token>`
  * `Content-Type: application/json`
* **Request Payload**:
  ```json
  {
    "status": "ACTIVE"
  }
  ```
* **Success Response**: `200 OK`

### 5. Delete Sprint
* **URL**: `/project/<uuid:workspace_id>/sprints/<uuid:sprint_id>/`
* **Method**: `DELETE`
* **Headers**:
  * `Authorization: Bearer <token>`
* **Access Control**: Requester must have active project access in the workspace.
* **Success Response**: `204 No Content`
  * Note: Deleting a sprint will not delete its associated tasks; they will be moved back to the backlog (`sprint` set to `null`).
