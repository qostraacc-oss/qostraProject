# Project Structure

## Project Overview
**QostraProjects** handles the task tracking, roadmaps, and timelogs for the Qostra ERP platform. It manages task allocations, Kanban boards, project milestone roadmaps, and positive-duration time logging. It securely handles cross-workspace user invitations, allowing external members to map invited projects to their own workspaces for clean separation of personal, freelance, and company contexts.

This document provides a detailed overview of the QostraProjects project directory structure and the purpose of each component.

## Root Directory
- `/apps/`: Contains custom Django applications managing project roadmaps, tasks, and timesheets.
- `/common/`: Shared exceptions, base models, permission classes, and helper utilities.
- `/config/`: Core configuration files, routing, and wsgi/asgi setups.
- `manage.py`: Django command-line execution helper.
- `pyproject.toml` / `uv.lock`: Dependency definitions controlled via `uv`.

## 1. Apps (`/apps/`)
Logic is partitioned into projects, milestones, tasks, timelogs, and sprints.

### Projects (`/projects/`)
Core workspace project management (status, owners, metadata, and invitations).
- `models/`: Package defining database models including `Project`, `ProjectMember`, and `ProjectInvitation`.
- `views/`: Package managing project, member, and invitation views.
- `serializers/`: Package handling project, member, and invitation data validation/serialization.
- `services/`: Encapsulates project management business services.

### Milestones (`/milestones/`)
Chronological roadmaps and phases for projects.
- `models.py`: Defines the `Milestone` model (deadlines, descriptions, associations).
- `views/`: Package managing milestone views.
- `serializers/`: Handles milestone data validation.
- `services/`: Encapsulates milestone timeline business services.

### Tasks (`/tasks/`)
Task items, assignment, Kanban boards, and task dependencies.
- `models/`: Package defining board, column, and task models.
- `views/`: Package managing board, column, and task views.
- `serializers/`: Package handling board, column, and task serializers.
- `services/`: Encapsulates task workflow business services.

### Timelogs (`/timelogs/`)
Timesheet logging and duration tracking.
- `models.py`: Defines the `TimeLog` model (hours, description, associations).
- `views/`: Package managing timelog views.
- `serializers/`: Handles timelog data validation.
- `services/`: Encapsulates timesheet business services.

### Sprints (`/sprints/`)
Iteration scheduling and time-boxed roadmaps.
- `models.py`: Defines the `Sprint` model (duration, status, associations).
- `views/`: Package managing sprint views.
- `serializers/`: Handles sprint data validation.


## 2. Common Components (`/common/`)
- `utils/`: Date range parsers, weekly timesheet aggregation helpers.
- `permissions/`: Project-specific permissions.
  - `mixins.py`: Defines the `WorkspaceResourceMixin` for resolving parent projects.
  - `workspace_permissions.py`: Defines the generic `HasWorkspaceProjectAccess` permission class.


## 3. Configuration (`/config/`)
- `settings/`: Multi-environment settings structure (`base.py`, `dev.py`, `prod.py`, `test.py`).

## 4. Documentation (`/.project/`)
- `project_rules.md`: Core developer rules and UV configurations.
- `project_structure.md`: This file.
- `api/`: Folder containing Markdown API documentation files for each application.
