import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project, ProjectMember
from tasks.models import Board, Column, Task

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


class TaskAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="taskuser",
            email="taskuser@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

        # Create a Project (This automatically creates self.user as an active project owner member)
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Task Test Project",
            code="TTP",
        )

        # Create a Board
        self.board = Board.objects.create(
            project=self.project,
            name="Development Board",
        )

        # Create two Columns
        self.col_todo = Column.objects.create(
            board=self.board,
            name="To Do",
            position=0,
            category=Column.Category.OPEN,
        )
        self.col_done = Column.objects.create(
            board=self.board,
            name="Done",
            position=1,
            category=Column.Category.DONE,
        )

    def test_list_tasks(self):
        # Create a task first
        Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="Setup DB",
            reporter=self.user,
        )

        url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Setup DB")
        self.assertEqual(response.data[0]["number"], 1)

    def test_create_task_api(self):
        url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "title": "Build UI Component",
            "type": "FEATURE",
            "column": self.col_todo.id,
            "priority": "HIGH",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Build UI Component")
        self.assertEqual(response.data["number"], 1)
        self.assertEqual(response.data["position"], 0)

        # Create another task to verify sequential numbering and auto-positioning
        data2 = {
            "title": "Write Unit Tests",
            "type": "TASK",
            "column": self.col_todo.id,
        }
        response2 = self.client.post(url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data["number"], 2)
        self.assertEqual(response2.data["position"], 1)

    def test_create_task_with_shifting(self):
        # Create task at position 0
        t1 = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="Task 1",
            position=0,
            reporter=self.user,
        )

        url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "title": "Task 2 (inserted at 0)",
            "column": self.col_todo.id,
            "position": 0,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["position"], 0)

        # Verify t1 was shifted to position 1
        t1.refresh_from_db()
        self.assertEqual(t1.position, 1)

    def test_update_task_validation(self):
        task = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="Check dates",
            reporter=self.user,
        )

        url = reverse(
            "task-detail",
            kwargs={"workspace_id": self.workspace_id, "task_id": task.id},
        )
        # Invalid date: due_date before start_date
        data = {
            "start_date": "2026-07-10",
            "due_date": "2026-07-05",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)

        # Block direct update of position and column
        response_pos = self.client.patch(url, {"position": 5}, format="json")
        self.assertEqual(response_pos.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_task_repositions_others(self):
        Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="T1",
            position=0,
            reporter=self.user,
        )
        t2 = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="T2",
            position=1,
            reporter=self.user,
        )
        t3 = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="T3",
            position=2,
            reporter=self.user,
        )

        url = reverse(
            "task-detail",
            kwargs={"workspace_id": self.workspace_id, "task_id": t2.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        t3.refresh_from_db()
        self.assertEqual(t3.position, 1)

    def test_move_task_within_column(self):
        t0 = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="T0",
            position=0,
            reporter=self.user,
        )
        t1 = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="T1",
            position=1,
            reporter=self.user,
        )
        t2 = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="T2",
            position=2,
            reporter=self.user,
        )

        url = reverse(
            "task-move",
            kwargs={"workspace_id": self.workspace_id, "task_id": t0.id},
        )
        # Move T0 to position 1
        response = self.client.patch(
            url,
            {"target_column_id": self.col_todo.id, "target_position": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        t0.refresh_from_db()
        t1.refresh_from_db()
        t2.refresh_from_db()

        self.assertEqual(t0.position, 1)
        self.assertEqual(t1.position, 0)
        self.assertEqual(t2.position, 2)

    def test_move_task_to_different_column(self):
        t_todo = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="Todo Task",
            position=0,
            reporter=self.user,
        )
        t_done1 = Task.objects.create(
            project=self.project,
            column=self.col_done,
            title="Done Task 1",
            position=0,
            reporter=self.user,
        )
        t_done2 = Task.objects.create(
            project=self.project,
            column=self.col_done,
            title="Done Task 2",
            position=1,
            reporter=self.user,
        )

        url = reverse(
            "task-move",
            kwargs={"workspace_id": self.workspace_id, "task_id": t_todo.id},
        )
        # Move t_todo to position 1 of Done column
        response = self.client.patch(
            url,
            {"target_column_id": self.col_done.id, "target_position": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        t_todo.refresh_from_db()
        t_done1.refresh_from_db()
        t_done2.refresh_from_db()

        self.assertEqual(t_todo.column, self.col_done)
        self.assertEqual(t_todo.position, 1)
        self.assertEqual(t_done1.position, 0)
        self.assertEqual(t_done2.position, 2)

    def test_non_member_access_forbidden(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=other_user)

        url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_only_sees_assigned_tasks(self):
        # Create a task assigned to project owner (self.user)
        Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="Owner Task",
            assignee=self.user,
            reporter=self.user,
        )

        # Create a second member
        member_user = User.objects.create_user(
            username="memberuser",
            email="member@example.com",
            password="testpassword123",
        )
        ProjectMember.objects.create(
            project=self.project,
            user=member_user,
            workspace_id=self.workspace_id,
            role=ProjectMember.RoleChoices.MEMBER,
        )

        # Reload project to clear cached active_member_ids
        fresh_project = Project.objects.get(pk=self.project.pk)

        # Create a task assigned to the new member
        Task.objects.create(
            project=fresh_project,
            column=self.col_todo,
            title="Member Task",
            assignee=member_user,
            reporter=self.user,
        )

        # 1. Check from Owner perspective (should see both tasks)
        url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        response_owner = self.client.get(url)
        self.assertEqual(response_owner.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_owner.data), 2)

        # 2. Check from Member perspective (should only see the task assigned to them)
        self.client.force_authenticate(user=member_user)
        response_member = self.client.get(url)
        self.assertEqual(response_member.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_member.data), 1)
        self.assertEqual(response_member.data[0]["title"], "Member Task")

    def test_member_cannot_modify_unassigned_tasks(self):
        # Task assigned to Owner (self.user)
        owner_task = Task.objects.create(
            project=self.project,
            column=self.col_todo,
            title="Owner Task",
            assignee=self.user,
            reporter=self.user,
        )

        # Create a second member
        member_user = User.objects.create_user(
            username="memberuser2",
            email="member2@example.com",
            password="testpassword123",
        )
        ProjectMember.objects.create(
            project=self.project,
            user=member_user,
            workspace_id=self.workspace_id,
            role=ProjectMember.RoleChoices.MEMBER,
        )

        # Authenticate as member
        self.client.force_authenticate(user=member_user)

        # 1. GET detail of Owner task should be forbidden (403)
        detail_url = reverse(
            "task-detail",
            kwargs={"workspace_id": self.workspace_id, "task_id": owner_task.id},
        )
        response_get = self.client.get(detail_url)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

        # 2. PATCH Owner task should be forbidden (403)
        response_patch = self.client.patch(
            detail_url, {"title": "Hacked Title"}, format="json"
        )
        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN)

        # 3. DELETE Owner task should be forbidden (403)
        response_delete = self.client.delete(detail_url)
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)

        # 4. MOVE Owner task should be forbidden (403)
        move_url = reverse(
            "task-move",
            kwargs={"workspace_id": self.workspace_id, "task_id": owner_task.id},
        )
        response_move = self.client.patch(
            move_url,
            {"target_column_id": self.col_todo.id, "target_position": 1},
            format="json",
        )
        self.assertEqual(response_move.status_code, status.HTTP_403_FORBIDDEN)


class LabelAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="labeluser",
            email="labeluser@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

        # Create a Project
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Label Test Project",
            code="LTP",
        )
        # Seed default board & column
        self.board = Board.objects.create(project=self.project, name="Board")
        self.column = Column.objects.create(board=self.board, name="To Do", position=0)

    def test_workspace_label_crud(self):
        # Create a workspace label
        url = reverse(
            "workspace-label-list-create",
            kwargs={"workspace_id": self.workspace_id},
        )
        data = {
            "name": "Global Bug",
            "color": "#EF4444",
            "description": "Critical issues",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Global Bug")
        self.assertIsNone(response.data["project"])

        label_id = response.data["id"]

        # Unique name constraint check
        response_dup = self.client.post(url, data, format="json")
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)

        # List workspace labels
        response_list = self.client.get(url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)

        # Get detail
        detail_url = reverse(
            "label-detail",
            kwargs={"workspace_id": self.workspace_id, "label_id": label_id},
        )
        response_detail = self.client.get(detail_url)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)

        # Update
        response_patch = self.client.patch(
            detail_url, {"name": "Global Issue"}, format="json"
        )
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.data["name"], "Global Issue")

        # Delete (archive)
        response_delete = self.client.delete(detail_url)
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

        # Fetching it should now return 404
        response_get_deleted = self.client.get(detail_url)
        self.assertEqual(response_get_deleted.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_label_creation(self):
        url = reverse(
            "project-label-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "name": "Niche Bug",
            "color": "#10B981",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Niche Bug")
        self.assertEqual(str(response.data["project"]), str(self.project.id))

    def test_hex_color_validation(self):
        url = reverse(
            "workspace-label-list-create",
            kwargs={"workspace_id": self.workspace_id},
        )
        # Invalid color
        response = self.client.post(
            url, {"name": "Bad Color", "color": "red"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_labels_to_task(self):
        from labels.models import Label

        # Create a workspace label and a project label
        ws_label = Label.objects.create(
            workspace_id=self.workspace_id,
            name="WS Label",
            color="#FF0000",
        )
        proj_label = Label.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            name="Proj Label",
            color="#00FF00",
        )
        # Create a label belonging to another workspace
        foreign_label = Label.objects.create(
            workspace_id=uuid.uuid4(),
            name="Foreign Label",
            color="#0000FF",
        )

        # Create Task
        task_url = reverse(
            "task-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        task_data = {
            "column": self.column.id,
            "title": "Task with Labels",
            "labels": [ws_label.id, proj_label.id],
        }
        response = self.client.post(task_url, task_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["labels"]), 2)

        # Attempt to assign foreign label
        task_data_bad = {
            "column": self.column.id,
            "title": "Task with Bad Labels",
            "labels": [foreign_label.id],
        }
        response_bad = self.client.post(task_url, task_data_bad, format="json")
        self.assertEqual(response_bad.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_labels_list(self):
        from labels.models import Label

        # Create a workspace-wide label
        Label.objects.create(
            workspace_id=self.workspace_id,
            name="Workspace Bug",
            color="#FF0000",
        )
        # Create a project-scoped label
        Label.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            name="Project Niche",
            color="#00FF00",
        )

        url = reverse("all-labels-list", kwargs={"workspace_id": self.workspace_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return both labels
        self.assertEqual(len(response.data), 2)
