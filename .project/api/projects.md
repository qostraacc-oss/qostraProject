# Projects API Reference

This application exposes endpoints for workspace-scoped project management and membership control.

---

## Base Path
All endpoints are prefixed with the workspace scope:
`/project/<uuid:workspace_id>/`

## Projects Endpoints

### 1. List Projects
* **URL**: `/project/<uuid:workspace_id>/`
* **Method**: `GET`
* **Headers**: 
  * `Authorization: Bearer <token>`
* **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "workspace_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
      "client_id": null,
      "created_by": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33",
      "created_by_username": "john_doe",
      "name": "Project Alpha",
      "slug": "project-alpha",
      "code": "ALPHA",
      "description": "Core workspace project.",
      "status": "planned",
      "priority": "medium",
      "start_date": "2026-06-12",
      "target_end_date": "2026-12-31",
      "actual_end_date": null,
      "archived_at": null,
      "created_at": "2026-06-12T12:00:00Z",
      "updated_at": "2026-06-12T12:00:00Z",
      "members": [
        {
          "id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44",
          "workspace_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
          "project": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
          "user": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33",
          "user_email": "john.doe@example.com",
          "user_username": "john_doe",
          "role": "owner",
          "created_by": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33",
          "removed_at": null,
          "created_at": "2026-06-12T12:00:00Z",
          "updated_at": "2026-06-12T12:00:00Z"
        }
      ]
    }
  ]
  ```

### 2. Create Project
* **URL**: `/project/<uuid:workspace_id>/`
* **Method**: `POST`
* **Headers**:
  * `Authorization: Bearer <token>`
  * `Content-Type: application/json`
* **Request Payload**:
  ```json
  {
    "name": "Project Alpha",
    "code": "ALPHA",
    "client_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", // optional
    "description": "Core workspace project.", // optional
    "status": "planned", // optional
    "priority": "medium", // optional
    "start_date": "2026-06-12", // optional
    "target_end_date": "2026-12-31", // optional
    "actual_end_date": null // optional
  }
  ```
* **Success Response**: `201 Created`
  * Returns the newly created Project JSON object. Note that the project creator is automatically assigned as the project `OWNER` in the member list.

### 3. Retrieve Project
* **URL**: `/project/<uuid:workspace_id>/<uuid:id>/`
* **Method**: `GET`
* **Success Response**: `200 OK`

### 4. Update Project (Partial)
* **URL**: `/project/<uuid:workspace_id>/<uuid:id>/`
* **Method**: `PATCH`
* **Success Response**: `200 OK`

### 5. Soft-Delete (Archive) Project
* **URL**: `/project/<uuid:workspace_id>/<uuid:id>/`
* **Method**: `DELETE`
* **Success Response**: `204 No Content`
  * Sets the `archived_at` timestamp.

---

## Project Members Endpoints

### 1. List Project Members
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/members/`
* **Method**: `GET`
* **Success Response**: `200 OK`

### 2. Retrieve Project Member
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/members/<uuid:id>/`
* **Method**: `GET`
* **Success Response**: `200 OK`

### 3. Remove Project Member (Soft-Delete)
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/members/<uuid:id>/`
* **Method**: `DELETE`
* **Success Response**: `204 No Content`
  * Sets the `removed_at` timestamp.
