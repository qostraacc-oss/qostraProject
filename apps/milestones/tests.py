import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project
from milestones.models import Milestone
from tasks.models import Board, Column, Task

User = get_user_model()


class MilestoneAPITestCase(TestCase):
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

        # Create Board & Column for task completion checks
        self.board = Board.objects.create(
            project=self.project,
            name="Test Board",
        )
        self.todo_column = Column.objects.create(
            board=self.board,
            name="To Do",
            category=Column.Category.OPEN,
            position=0,
        )
        self.done_column = Column.objects.create(
            board=self.board,
            name="Done",
            category=Column.Category.DONE,
            position=1,
        )

    def test_create_milestone_api(self):
        url = reverse(
            "milestone-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "name": "Milestone 1",
            "description": "First milestone",
            "start_date": "2026-07-01",
            "due_date": "2026-07-15",
            "status": "planned",
            "color": "blue",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Milestone 1")
        self.assertEqual(response.data["position"], 0)  # Auto-position starts at 0

        # Create second milestone to check auto-incrementing position
        data2 = {
            "name": "Milestone 2",
            "status": "active",
        }
        response2 = self.client.post(url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data["position"], 1)

        # Create a third milestone explicitly at position 0 to verify shifting
        data3 = {
            "name": "Milestone Zero",
            "status": "planned",
            "position": 0,
        }
        response3 = self.client.post(url, data3, format="json")
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response3.data["position"], 0)

        # Verify that Milestone 1 and Milestone 2 have shifted positions to 1 and 2
        response_list = self.client.get(url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        # Sequence should now be: Milestone Zero (pos 0), Milestone 1 (pos 1), Milestone 2 (pos 2)
        self.assertEqual(response_list.data[0]["name"], "Milestone Zero")
        self.assertEqual(response_list.data[0]["position"], 0)
        self.assertEqual(response_list.data[1]["name"], "Milestone 1")
        self.assertEqual(response_list.data[1]["position"], 1)
        self.assertEqual(response_list.data[2]["name"], "Milestone 2")
        self.assertEqual(response_list.data[2]["position"], 2)

        # Attempting to create a milestone at position 10 (gap) should fail
        data_gap = {
            "name": "Gap Milestone",
            "position": 10,
        }
        response_gap = self.client.post(url, data_gap, format="json")
        self.assertEqual(response_gap.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("position", response_gap.data)

    def test_milestone_validation_dates(self):
        url = reverse(
            "milestone-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "name": "Invalid Dates Milestone",
            "start_date": "2026-07-15",
            "due_date": "2026-07-01",  # due_date is before start_date
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)

    def test_list_milestones_filtering_and_sorting(self):
        Milestone.objects.create(
            project=self.project,
            name="Milestone Alpha",
            position=2,
            due_date="2026-07-20",
            status="active",
            created_by=self.user,
        )
        Milestone.objects.create(
            project=self.project,
            name="Milestone Beta",
            position=1,
            due_date="2026-07-10",
            status="planned",
            created_by=self.user,
        )
        Milestone.objects.create(
            project=self.project,
            name="Milestone Archived",
            position=3,
            archived_at=timezone.now(),
            created_by=self.user,
        )

        url = reverse(
            "milestone-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )

        # Default list (excludes archived, ordered by position asc: Beta then Alpha)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Milestone Beta")
        self.assertEqual(response.data[1]["name"], "Milestone Alpha")

        # Include archived
        response_archived = self.client.get(f"{url}?include_archived=true")
        self.assertEqual(response_archived.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_archived.data), 3)

        # Filter by status
        response_status = self.client.get(f"{url}?status=active")
        self.assertEqual(response_status.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_status.data), 1)
        self.assertEqual(response_status.data[0]["name"], "Milestone Alpha")

        # Order by due_date
        response_order = self.client.get(f"{url}?ordering=due_date")
        self.assertEqual(response_order.status_code, status.HTTP_200_OK)
        self.assertEqual(response_order.data[0]["name"], "Milestone Beta")  # 2026-07-10
        self.assertEqual(
            response_order.data[1]["name"], "Milestone Alpha"
        )  # 2026-07-20

    def test_milestone_detail_and_completed_at(self):
        milestone = Milestone.objects.create(
            project=self.project,
            name="Milestone 1",
            status="active",
            created_by=self.user,
        )

        detail_url = reverse(
            "milestone-detail",
            kwargs={"workspace_id": self.workspace_id, "milestone_id": milestone.id},
        )

        # Get detail
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["completed_at"])

        # Patch to completed
        response_patch = self.client.patch(
            detail_url, {"status": "completed"}, format="json"
        )
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response_patch.data["completed_at"])

        # Patch back to active
        response_patch_back = self.client.patch(
            detail_url, {"status": "active"}, format="json"
        )
        self.assertEqual(response_patch_back.status_code, status.HTTP_200_OK)
        self.assertIsNone(response_patch_back.data["completed_at"])

        # Direct patch to position should be blocked
        response_patch_pos = self.client.patch(
            detail_url, {"position": 5}, format="json"
        )
        self.assertEqual(response_patch_pos.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("position", response_patch_pos.data)

    def test_milestone_delete_archives_instead_of_removing(self):
        m1 = Milestone.objects.create(
            project=self.project,
            name="M1",
            position=0,
            created_by=self.user,
        )
        m2 = Milestone.objects.create(
            project=self.project,
            name="M2 (To Delete)",
            position=1,
            created_by=self.user,
        )
        m3 = Milestone.objects.create(
            project=self.project,
            name="M3",
            position=2,
            created_by=self.user,
        )

        detail_url = reverse(
            "milestone-detail",
            kwargs={"workspace_id": self.workspace_id, "milestone_id": m2.id},
        )

        # DELETE request (should archive m2)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert in DB that m2 is archived and position is cleared
        m2.refresh_from_db()
        self.assertIsNotNone(m2.archived_at)
        self.assertTrue(m2.is_archived)
        self.assertIsNone(m2.position)

        # Assert that m3 has shifted from position 2 to position 1
        m3.refresh_from_db()
        self.assertEqual(m3.position, 1)

        # Assert that m1 remains at position 0
        m1.refresh_from_db()
        self.assertEqual(m1.position, 0)

        # Create active milestone with the same name as the archived milestone (should succeed)
        create_url = reverse(
            "milestone-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response_reuse = self.client.post(
            create_url, {"name": "M2 (To Delete)"}, format="json"
        )
        self.assertEqual(response_reuse.status_code, status.HTTP_201_CREATED)

        # Attempt to create active milestone with same name as active milestone "M1" (should fail)
        response_dup = self.client.post(create_url, {"name": "M1"}, format="json")
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response_dup.data)

    def test_reorder_milestones_api(self):
        m1 = Milestone.objects.create(
            project=self.project, name="M1", position=0, created_by=self.user
        )
        m2 = Milestone.objects.create(
            project=self.project, name="M2", position=1, created_by=self.user
        )

        url = reverse(
            "milestone-reorder",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = [
            {"id": str(m1.id), "position": 1},
            {"id": str(m2.id), "position": 0},
        ]
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m1.refresh_from_db()
        m2.refresh_from_db()
        self.assertEqual(m1.position, 1)
        self.assertEqual(m2.position, 0)

    def test_task_metrics_on_milestone(self):
        milestone = Milestone.objects.create(
            project=self.project,
            name="Sprint Milestone",
            created_by=self.user,
        )

        # Create tasks linked to this milestone
        # Task 1: OPEN, not overdue
        Task.objects.create(
            project=self.project,
            column=self.todo_column,
            title="Task 1",
            milestone=milestone,
            reporter=self.user,
            due_date=timezone.now().date() + timezone.timedelta(days=5),
        )
        # Task 2: DONE
        Task.objects.create(
            project=self.project,
            column=self.done_column,
            title="Task 2",
            milestone=milestone,
            reporter=self.user,
        )
        # Task 3: OPEN, overdue (due_date in past)
        Task.objects.create(
            project=self.project,
            column=self.todo_column,
            title="Task 3",
            milestone=milestone,
            reporter=self.user,
            due_date=timezone.now().date() - timezone.timedelta(days=2),
        )

        detail_url = reverse(
            "milestone-detail",
            kwargs={"workspace_id": self.workspace_id, "milestone_id": milestone.id},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert calculated metrics in serializer response
        self.assertEqual(response.data["task_count"], 3)
        self.assertEqual(response.data["completed_task_count"], 1)
        self.assertEqual(response.data["overdue_task_count"], 1)
        # progress = (1 / 3) * 100 = 33.33%
        self.assertEqual(response.data["progress"], 33.33)

    def test_task_milestone_project_and_workspace_alignment(self):
        other_project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Other Project",
            code="OTH",
        )
        other_milestone = Milestone.objects.create(
            project=other_project,
            name="Other Milestone",
            created_by=self.user,
        )

        task_url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )

        # Attempt to link other_milestone to a task in self.project
        task_data = {
            "title": "New Task",
            "column": str(self.todo_column.id),
            "milestone": str(other_milestone.id),
        }
        response = self.client.post(task_url, task_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("milestone", response.data)

    def test_permissions_enforced(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="password123",
        )
        # Authentication using a non-member user
        self.client.force_authenticate(user=other_user)

        url = reverse(
            "milestone-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
