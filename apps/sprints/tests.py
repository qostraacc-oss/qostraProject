import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from projects.models import Project
from sprints.models import Sprint
from tasks.models import Board, Column, Task

User = get_user_model()


class SprintAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

        # Create project
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Test Project",
            code="TEST",
        )

        # Board and Column for Task
        self.board = Board.objects.create(
            project=self.project,
            name="Test Board",
        )
        self.column = Column.objects.create(
            board=self.board,
            name="To Do",
            category=Column.Category.OPEN,
            position=0,
        )

    def test_create_sprint_api(self):
        url = reverse(
            "sprint-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "name": "Sprint 1",
            "goal": "Deliver auth",
            "start_date": "2026-07-20",
            "end_date": "2026-08-03",
            "status": "PLANNED",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Sprint 1")

    def test_list_sprints_api(self):
        Sprint.objects.create(
            project=self.project,
            name="Sprint 1",
            start_date="2026-07-20",
            end_date="2026-08-03",
        )
        url = reverse(
            "sprint-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_sprint_api(self):
        sprint = Sprint.objects.create(
            project=self.project,
            name="Sprint 1",
            start_date="2026-07-20",
            end_date="2026-08-03",
        )
        url = reverse(
            "sprint-detail",
            kwargs={"workspace_id": self.workspace_id, "sprint_id": sprint.id},
        )
        data = {"name": "Sprint 1 Updated", "status": "ACTIVE"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Sprint 1 Updated")
        self.assertEqual(response.data["status"], "ACTIVE")

    def test_delete_sprint_and_backlog_retention(self):
        sprint = Sprint.objects.create(
            project=self.project,
            name="Sprint 1",
            start_date="2026-07-20",
            end_date="2026-08-03",
        )
        task = Task.objects.create(
            project=self.project,
            title="Sprint Task",
            column=self.column,
            sprint=sprint,
            reporter=self.user,
        )
        url = reverse(
            "sprint-detail",
            kwargs={"workspace_id": self.workspace_id, "sprint_id": sprint.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Task should remain but its sprint reference is NULL
        task.refresh_from_db()
        self.assertNil = self.assertIsNone(task.sprint)

    def test_cross_project_sprint_validation(self):
        other_project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Other Project",
            code="OTH",
        )
        sprint = Sprint.objects.create(
            project=other_project,
            name="Other Sprint",
            start_date="2026-07-20",
            end_date="2026-08-03",
        )

        task = Task(
            project=self.project,
            title="Sprint Task",
            column=self.column,
            sprint=sprint,
            reporter=self.user,
        )
        # Should raise ValidationError due to project mismatch
        with self.assertRaises(ValidationError):
            task.clean()
