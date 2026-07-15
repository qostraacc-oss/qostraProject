import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project
from tasks.models import Board, Column, Task
from timelogs.models import TimeLog

User = get_user_model()


class TimeLogAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="timeloguser",
            email="timeloguser@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

        # Create Project
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Timelog Test Project",
            code="TLP",
        )

        # Create Board & Column
        self.board = Board.objects.create(
            project=self.project,
            name="Test Board",
        )
        self.column = Column.objects.create(
            board=self.board,
            name="In Progress",
            position=1,
        )

        # Create Task
        self.task = Task.objects.create(
            project=self.project,
            column=self.column,
            title="Integrate Sentry SDK",
            reporter=self.user,
            assignee=self.user,
            estimate=Decimal("10.00"),
        )

    def test_create_and_list_timelogs_api(self):
        url = reverse(
            "timelog-list-create",
            kwargs={"workspace_id": self.workspace_id, "task_id": self.task.id},
        )
        data = {
            "duration": "4.50",
            "description": "Configured middleware and error handler.",
        }

        # Test creation
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["duration"], "4.50")

        # Verify Task time_spent updated automatically
        self.task.refresh_from_db()
        self.assertEqual(self.task.time_spent, Decimal("4.50"))

        # Test listing
        response_list = self.client.get(url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)
        self.assertEqual(
            response_list.data[0]["description"],
            "Configured middleware and error handler.",
        )

    def test_negative_duration_validation(self):
        url = reverse(
            "timelog-list-create",
            kwargs={"workspace_id": self.workspace_id, "task_id": self.task.id},
        )
        data = {
            "duration": "-2.00",
            "description": "Invalid log",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_and_delete_timelogs(self):
        # Create a log directly
        log = TimeLog.objects.create(
            task=self.task,
            user=self.user,
            duration=Decimal("3.00"),
            description="Working on sentry setup",
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.time_spent, Decimal("3.00"))

        # Test update API
        url = reverse(
            "timelog-detail",
            kwargs={"workspace_id": self.workspace_id, "pk": log.id},
        )
        data = {"duration": "5.00"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertEqual(self.task.time_spent, Decimal("5.00"))

        # Test delete API
        response_delete = self.client.delete(url)
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

        self.task.refresh_from_db()
        self.assertEqual(self.task.time_spent, Decimal("0.00"))

    def test_locked_timelog_restriction(self):
        log = TimeLog.objects.create(
            task=self.task,
            user=self.user,
            duration=Decimal("2.00"),
            description="Billing period log",
            is_locked=True,
        )

        url = reverse(
            "timelog-detail",
            kwargs={"workspace_id": self.workspace_id, "pk": log.id},
        )

        # Attempt to update via API should fail
        response_update = self.client.patch(url, {"duration": "3.00"}, format="json")
        self.assertEqual(response_update.status_code, status.HTTP_400_BAD_REQUEST)

        # Attempt to delete via API should fail
        response_delete = self.client.delete(url)
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        # Attempt to save or delete programmatically should raise ValidationError
        with self.assertRaises(ValidationError):
            log.duration = Decimal("3.00")
            log.save()

        with self.assertRaises(ValidationError):
            log.delete()
