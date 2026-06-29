import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project
from tasks.models import Board, Column

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

        # Verify default columns are seeded
        board_id = response.data["id"]
        columns_count = Column.objects.filter(board_id=board_id).count()
        self.assertEqual(columns_count, 3)

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


class ColumnAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="columnuser",
            email="columnuser@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

        # Create a Project
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Column Test Project",
            code="CTP",
        )

        # Create a Board
        self.board = Board.objects.create(
            project=self.project,
            name="Sprint Board",
            description="Sprint board for column testing",
        )

        # Create a Column
        self.column = Column.objects.create(
            board=self.board,
            name="To Do",
            position=0,
            category=Column.Category.OPEN,
            color="#9CA3AF",
        )

    def test_list_columns_api(self):
        url = reverse(
            "column-list-create",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "To Do")

    def test_create_column_api(self):
        url = reverse(
            "column-list-create",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        data = {
            "name": "In Progress",
            "position": 1,
            "category": "OPEN",
            "color": "#3B82F6",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "In Progress")

        # Verify unique name constraint per board
        response_dup = self.client.post(url, data, format="json")
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)

    def test_column_detail_api(self):
        url = reverse(
            "column-detail",
            kwargs={"workspace_id": self.workspace_id, "column_id": self.column.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "To Do")

    def test_update_column_api(self):
        url = reverse(
            "column-detail",
            kwargs={"workspace_id": self.workspace_id, "column_id": self.column.id},
        )
        data = {"name": "Backlog"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Backlog")
        self.assertEqual(response.data["position"], 0)

    def test_delete_column_api(self):
        url = reverse(
            "column-detail",
            kwargs={"workspace_id": self.workspace_id, "column_id": self.column.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Column.objects.filter(id=self.column.id).exists())

    def test_access_denied_for_non_members(self):
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=other_user)

        url = reverse(
            "column-list-create",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_column_autoposition(self):
        url = reverse(
            "column-list-create",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        # Create a second column without specifying position
        data = {
            "name": "Review",
            "category": "OPEN",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Since the first column has position 0, this should auto-assign to 1
        self.assertEqual(response.data["position"], 1)

    def test_reorder_columns_api(self):
        # Create some additional columns for reordering
        col2 = Column.objects.create(
            board=self.board,
            name="In Progress",
            position=1,
            category=Column.Category.OPEN,
        )
        col3 = Column.objects.create(
            board=self.board,
            name="Done",
            position=2,
            category=Column.Category.DONE,
        )

        url = reverse(
            "column-reorder",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        # New desired order: col3, self.column, col2
        data = {"column_ids": [col3.id, self.column.id, col2.id]}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify positions are updated: 0, 1, 2
        col3.refresh_from_db()
        self.column.refresh_from_db()
        col2.refresh_from_db()

        self.assertEqual(col3.position, 0)
        self.assertEqual(self.column.position, 1)
        self.assertEqual(col2.position, 2)

    def test_create_column_with_shifting(self):
        # Current board has self.column at position 0.
        col2 = Column.objects.create(
            board=self.board,
            name="In Progress",
            position=1,
            category=Column.Category.OPEN,
        )

        # POST a new column at position 1.
        url = reverse(
            "column-list-create",
            kwargs={"workspace_id": self.workspace_id, "board_id": self.board.id},
        )
        data = {
            "name": "Design Review",
            "position": 1,
            "category": "OPEN",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        col2.refresh_from_db()
        self.column.refresh_from_db()

        self.assertEqual(response.data["position"], 1)
        self.assertEqual(col2.position, 2)
        self.assertEqual(self.column.position, 0)

    def test_update_column_position_is_blocked(self):
        url = reverse(
            "column-detail",
            kwargs={"workspace_id": self.workspace_id, "column_id": self.column.id},
        )
        data = {"position": 2}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("position", response.data)

    def test_delete_column_repositions_others(self):
        col2 = Column.objects.create(
            board=self.board,
            name="In Progress",
            position=1,
            category=Column.Category.OPEN,
        )
        col3 = Column.objects.create(
            board=self.board,
            name="Done",
            position=2,
            category=Column.Category.DONE,
        )

        url = reverse(
            "column-detail",
            kwargs={"workspace_id": self.workspace_id, "column_id": col2.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        col3.refresh_from_db()
        self.column.refresh_from_db()

        self.assertEqual(col3.position, 1)
        self.assertEqual(self.column.position, 0)
