import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project, ProjectMember, ProjectInvitation
from tasks.models import Board

User = get_user_model()


class WorkspaceMappingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username="owneruser", email="owner@example.com", password="testpassword123"
        )
        self.owner_workspace = uuid.uuid4()
        
        self.project = Project.objects.create(
            workspace_id=self.owner_workspace,
            created_by=self.owner,
            name="Project Gamma",
            code="GAMMA",
        )

        self.invitee = User.objects.create_user(
            username="inviteeuser", email="invitee@example.com", password="testpassword123"
        )
        self.invitee_workspace_mapped = uuid.uuid4()
        self.invitee_workspace_other = uuid.uuid4()

        # Create Board under the project
        self.board = Board.objects.create(
            project=self.project,
            name="Sprint Board"
        )

    def test_workspace_mapping_and_isolation(self):
        # 1. Create invitation
        invite = ProjectInvitation.objects.create(
            workspace_id=self.owner_workspace,
            project=self.project,
            invitee_id=self.invitee.id,
            invitee_email=self.invitee.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )

        # 2. Accept invitation and map to target workspace
        self.client.force_authenticate(user=self.invitee)
        accept_url = reverse("project-invitation-accept", kwargs={"invitation_id": invite.id})
        
        # Test validation: workspace_id required
        response = self.client.post(accept_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("workspace_id", response.data)

        # Accept successfully mapping to invitee_workspace_mapped
        response = self.client.post(
            accept_url, 
            data={"workspace_id": str(self.invitee_workspace_mapped)}, 
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify membership record
        member = ProjectMember.objects.get(project=self.project, user=self.invitee)
        self.assertEqual(member.workspace_id, self.invitee_workspace_mapped)

        # 3. Verify project visibility on mapped workspace
        list_url_mapped = reverse("project-list-create", kwargs={"workspace_id": self.invitee_workspace_mapped})
        response = self.client.get(list_url_mapped)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.project.id))

        # 4. Verify project is hidden from other workspace
        list_url_other = reverse("project-list-create", kwargs={"workspace_id": self.invitee_workspace_other})
        response = self.client.get(list_url_other)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # 5. Verify board retrieval works in mapped workspace context
        board_url_mapped = reverse(
            "board-detail", 
            kwargs={"workspace_id": self.invitee_workspace_mapped, "board_id": self.board.id}
        )
        response = self.client.get(board_url_mapped)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Sprint Board")

        # 6. Verify board retrieval fails with 404 in unmapped workspace context
        board_url_other = reverse(
            "board-detail", 
            kwargs={"workspace_id": self.invitee_workspace_other, "board_id": self.board.id}
        )
        response = self.client.get(board_url_other)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 7. Verify Owner (Workspace A) can still view and manage the membership
        self.client.force_authenticate(user=self.owner)
        member_detail_url = reverse(
            "project-member-detail",
            kwargs={
                "workspace_id": self.owner_workspace,
                "project_id": self.project.id,
                "pk": member.id
            }
        )
        # Owner can retrieve the member detail
        response = self.client.get(member_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(member.id))
