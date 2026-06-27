# Project Rules

This document outlines the core development rules and best practices for the QostraProjects project. All developers and AI agents MUST adhere to these rules.

> [!IMPORTANT]
> **AI AGENT DIRECTIVE**: Any AI agent interacting with this codebase MUST read both `project_rules.md` and `project_structure.md` before making any changes or analysis.

## 1. Core Structural Rules
- **Localized Logic**: Keep task helpers or timeline calculations inside their respective app folders (e.g. `apps/milestones/utils/`).
- **Shared Utilities**: Place globally shared filters (e.g. date-range filter class) in the `/common/` package.
- **Package Organization**: Organize views and serializers inside Python packages (`views/` directory with `__init__.py`) instead of monolithic single files.

## 2. Business Flow and Transitions
- **State Machine Integrity**: Ensure that status changes for projects and tasks follow valid state flows. Do not allow completed/archived tasks to be modified without proper verification.
- **Assigned User Scoping**: Users should only be allowed to modify task status or log time if they are assigned to the task/project, or hold manager/admin roles.
- **Logged Time Validation**: All logged time durations MUST be positive. Timelogs MUST be associated with a valid task and user, and should be locked/closed once a billing period ends.
- **Cross-Workspace Project Mapping**: When querying projects or project sub-resources (like boards, tasks, milestones) within a workspace context, you MUST use `Project.objects.for_workspace(workspace_id, user)` instead of filtering by `project__workspace_id` directly, to support external projects mapped to the member's workspace.


## 3. Code Quality and Maintenance
- **Consistency**: Maintain uniformity with serializers and views.
- **Optimized Queries**: Fetching kanban boards can generate massive N+1 queries. Always prefetch task assignees, tags, and milestones.
- **Documentation**: Keep project rules and structure docs updated.
  - **API Documentation**: Whenever a route is modified, added, or a request/response schema is changed, the corresponding API document inside `.project/api/` MUST be updated immediately.

## 4. Deployment and Environment
- **Security Check**: Always run `python manage.py check --deploy` before production rollouts.
- **Dependency Management**: Use `uv` for package management. Keep `pyproject.toml` and `uv.lock` updated, and avoid using raw `pip` commands.
  - Sync local environment: `uv sync`
  - Add dependency: `uv add <package>`
  - Remove dependency: `uv remove <package>`
  - Run Django commands: `uv run python manage.py <command>`

## 5. Code Quality, Linting & Testing Guidelines
- **Linting & Formatting (Ruff)**:
  - All Python code MUST be formatted and linted using `ruff`. Run `uv run ruff format` and `uv run ruff check` before committing.
- **Type Checking (MyPy)**:
  - Keep types clean and run type checks with `uv run mypy .` (configured with `django-stubs`).
- **Testing (PyTest)**:
  - All test suites MUST use `pytest` and `pytest-django`. Run tests with `uv run pytest`.
  - Use `factory-boy` and `faker` for generating mock database records in tests. Never hardcode static fixtures for dynamic test data.
- **Error Tracking & Rate Limiting**:
  - Production deployments MUST have `sentry-sdk` initialized in production settings.
  - Apply `django-ratelimit` decorators on public or sensitive API views (e.g., login, registration endpoints) to prevent brute-force attacks.
- **Debugging (Django Debug Toolbar)**:
  - Keep `django-debug-toolbar` enabled only in `dev.py` settings and ensure it is never exposed in production.
