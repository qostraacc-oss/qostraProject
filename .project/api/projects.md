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
* **Access Control**: Returns only the active projects where the authenticated user is an active member or the creator.
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
* **Access Control**: Requester must be the project creator or an active project member.
* **Success Response**: `200 OK`

### 4. Update Project (Partial)
* **URL**: `/project/<uuid:workspace_id>/<uuid:id>/`
* **Method**: `PATCH`
* **Access Control**: Only the project creator or an active project member with role `owner` or `admin` can perform updates.
* **Success Response**: `200 OK`

### 5. Soft-Delete (Archive) Project
* **URL**: `/project/<uuid:workspace_id>/<uuid:id>/`
* **Method**: `DELETE`
* **Access Control**: Only the project creator or the project `owner` member can archive the project.
* **Success Response**: `204 No Content`
  * Sets the `archived_at` timestamp.

---

## Project Members Endpoints

### 1. List Project Members
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/members/`
* **Method**: `GET`
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
* **Success Response**: `200 OK`

### 2. Retrieve Project Member
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/members/<uuid:id>/`
* **Method**: `GET`
* **Access Control**: Creator + `owner`, `admin`, `member`, `viewer` roles.
* **Success Response**: `200 OK`

### 3. Remove Project Member (Soft-Delete)
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/members/<uuid:id>/`
* **Method**: `DELETE`
* **Access Control**: Creator + `owner`, `admin` roles.
* **Success Response**: `204 No Content`
  * Sets the `removed_at` timestamp.


---

## Project Invitations Endpoints

### 1. List/Create Project Invitations
* **URL**: `/project/<uuid:workspace_id>/<uuid:project_id>/invitations/`
* **Methods**:
  * `GET`: Lists all invitations (pending, accepted, declined, revoked) sent for this project. Requester must be a member of the project.
  * `POST`: Sends a new project membership invitation. Requester must be a project owner or admin.
* **POST Request Payload**:
  ```json
  {
    "invitee_email": "target.user@qostra.com",
    "role": "member" // owner, admin, member, viewer
  }
  ```
* **Success Responses**:
  * `GET`: `200 OK`
  * `POST`: `201 Created`

### 2. Resend Invitation
* **URL**: `/project/<uuid:workspace_id>/invitations/<uuid:invitation_id>/resend/`
* **Method**: `POST`
* **Permission**: Requester must be a project owner or admin.
* **Success Response**: `200 OK` (returns the updated invitation object with a renewed `expires_at` timestamp).

### 3. Revoke Invitation
* **URL**: `/project/<uuid:workspace_id>/invitations/<uuid:invitation_id>/revoke/`
* **Method**: `POST`
* **Permission**: Requester must be a project owner or admin.
* **Success Response**: `200 OK` (updates status to `revoked` and records `revoked_at` timestamp).

### 4. Accept Invitation
* **URL**: `/project/invitations/<uuid:invitation_id>/accept/`
* **Method**: `POST`
* **Permission**: Requester must be the target invitee.
* **Request Payload**:
  ```json
  {
    "workspace_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22" // Mapped Workspace ID for the member
  }
  ```
* **Success Response**: `200 OK` (creates the `ProjectMember` record mapped to the selected workspace, updates invitation status to `accepted` and records `accepted_at`).

### 5. Decline Invitation
* **URL**: `/project/invitations/<uuid:invitation_id>/decline/`
* **Method**: `POST`
* **Permission**: Requester must be the target invitee.
* **Success Response**: `200 OK` (updates invitation status to `declined` and records `declined_at`).

### 6. User-Level Pending Invitations
* **URL**: `/project/invitations/`
* **Method**: `GET`
* **Permission**: Authenticated user.
* **Success Response**: `200 OK` (returns list of all `pending` invitations sent to the authenticated user).

### 7. User-Level Invitation Detail
* **URL**: `/project/invitations/<uuid:invitation_id>/`
* **Method**: `GET`
* **Permission**: Target invitee only.
* **Success Response**: `200 OK` (returns details of the specified invitation, useful for invitation accept screens).

### 8. Workspace-Level Invitation Detail
* **URL**: `/project/<uuid:workspace_id>/invitations/<uuid:invitation_id>/`
* **Method**: `GET`
* **Permission**: Project Owner or Admin within the workspace.
* **Success Response**: `200 OK` (returns details of the specified invitation).

