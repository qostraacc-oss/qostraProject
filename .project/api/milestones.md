# Milestones API Reference

This application exposes endpoints for project-specific milestone roadmaps, task associations, sequencing positions, and progress health metrics.

---

## Base Path
All endpoints are prefixed with the workspace scope:
`/project/<uuid:workspace_id>/`

## Milestones Endpoints

### 1. List Milestones
* **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/milestones/`
* **Method**: `GET`
* **Headers**: 
  * `Authorization: Bearer <token>`
* **Query Parameters**:
  * `include_archived=true`: (Optional) If set to true, includes soft-deleted/archived milestones. Default is false.
  * `status=<string>`: (Optional) Filter milestones by status: `planned`, `active`, `completed`, or `cancelled`.
  * `ordering=<string>`: (Optional) Order milestones by fields. Supported fields: `position`, `-position`, `due_date`, `-due_date`. Default is `position`.
* **Access Control**: Requires workspace membership and active project access.
* **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "project": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "name": "Phase 1: Backend Setup",
      "description": "Establish Django microservices, db schemas, and basic migrations.",
      "start_date": "2026-07-01",
      "due_date": "2026-07-15",
      "completed_at": null,
      "status": "active",
      "position": 0,
      "color": "blue",
      "archived_at": null,
      "is_archived": false,
      "created_by": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33",
      "created_by_username": "john_doe",
      "progress": 33.33,
      "task_count": 3,
      "completed_task_count": 1,
      "overdue_task_count": 1,
      "created_at": "2026-07-01T12:00:00Z",
      "updated_at": "2026-07-03T15:00:00Z"
    }
  ]
  ```

### 2. Create Milestone
* **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/milestones/`
* **Method**: `POST`
* **Headers**:
  * `Authorization: Bearer <token>`
  * `Content-Type: application/json`
* **Request Payload**:
  ```json
  {
    "name": "Phase 1: Backend Setup",
    "description": "Establish Django microservices.",
    "start_date": "2026-07-01", // optional
    "due_date": "2026-07-15", // optional
    "status": "planned", // optional
    "color": "blue", // optional
    "position": 0 // optional (must be contiguous: <= next available sequence index)
  }
  ```
* **Validation Rules**:
  * **Active Name Uniqueness**: Milestone name must be unique within the project among *active (non-archived)* milestones. Re-using a name from an archived milestone is permitted.
  * **Contiguous Positioning**: If `position` is provided, it cannot exceed the next available sequence index (e.g. if positions `0, 1, 2` exist, `position` must be `<= 3`).
  * **Automatic Shifting**: If a valid position is provided (e.g. `0`), the milestone is inserted there, and all subsequent active milestones' positions are automatically shifted up by 1. If not provided, it is automatically appended to the end of the active sequence.
* **Success Response**: `201 Created`
  * Returns the newly created Milestone JSON object.

### 3. Retrieve Milestone Detail
* **URL**: `/project/<uuid:workspace_id>/milestones/<uuid:milestone_id>/`
* **Method**: `GET`
* **Headers**:
  * `Authorization: Bearer <token>`
* **Access Control**: Requester must have active project access in the workspace.
* **Success Response**: `200 OK`

### 4. Update Milestone (Partial)
* **URL**: `/project/<uuid:workspace_id>/milestones/<uuid:milestone_id>/`
* **Method**: `PATCH`
* **Headers**:
  * `Authorization: Bearer <token>`
  * `Content-Type: application/json`
* **Request Payload**:
  ```json
  {
    "status": "completed"
  }
  ```
* **Success Response**: `200 OK`
  * Note: Transitioning status to `completed` automatically populates the `completed_at` timestamp. Transitioning away from `completed` resets `completed_at` to `null`.
  * Note: Direct modifications to the `position` field via `PATCH` are blocked with a `400 Bad Request` validation error. Always use the `/reorder/` endpoint to change positions.

### 5. Archive (Soft-Delete) Milestone
* **URL**: `/project/<uuid:workspace_id>/milestones/<uuid:milestone_id>/`
* **Method**: `DELETE`
* **Headers**:
* `Authorization: Bearer <token>`
* **Access Control**: Requires owner or admin project role.
* **Success Response**: `204 No Content`
  * Sets the `archived_at` timestamp. Does not physically delete the record from the database.
  * Clears the archived milestone's `position` to `null` and automatically shifts all subsequent active milestones' positions down to fill the gap.

### 6. Reorder Milestones Sequence
* **URL**: `/project/<uuid:workspace_id>/projects/<uuid:project_id>/milestones/reorder/`
* **Method**: `PATCH`
* **Headers**:
  * `Authorization: Bearer <token>`
  * `Content-Type: application/json`
* **Request Payload**:
  ```json
  [
    {
      "id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "position": 1
    },
    {
      "id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
      "position": 0
    }
  ]
  ```
* **Success Response**: `200 OK`
  ```json
  {
    "status": "success"
  }
  ```
