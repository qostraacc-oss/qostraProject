import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project
from tasks.models import Board

User = get_user_model()


class BoardAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="boarduser",
            email="boarduser@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

        # Create a Project
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Board Test Project",
            code="BTP",
        )

        # Create a Board
        self.board = Board.objects.create(
            project=self.project,
            name="Sprint Board",
            description="Sprint board for testing",
        )

    def test_list_boards_api(self):
        url = reverse(
            "board-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Sprint Board")

    def test_create_board_api(self):
        url = reverse(
            "board-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "name": "Backlog Board",
            "description": "Backlog board for tracking ideas",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Backlog Board")

        # Verify unique name constraint
        response_dup = self.client.post(url, data, format="json")
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)

    def test_board_detail_api(self):
        url = reverse(
            "board-detail",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Sprint Board")

    def test_update_board_api(self):
        url = reverse(
            "board-detail",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        data = {"name": "Updated Board Name"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Board Name")

    def test_delete_board_api(self):
        url = reverse(
            "board-detail",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(id=self.board.id).exists())

    def test_access_denied_for_non_members(self):
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=other_user)

        url = reverse(
            "board-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
