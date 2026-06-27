import uuid
import unittest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project, ProjectMember, ProjectInvitation

User = get_user_model()


class ProjectInvitationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username="owneruser", email="owner@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.owner)
        self.workspace_id = uuid.uuid4()

        # Create project (owner is automatically added as Owner member)
        self.project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.owner,
            name="Project Gamma",
            code="GAMMA",
        )

        # Create target user to invite
        self.target_user = User.objects.create_user(
            username="targetuser",
            email="target@example.com",
            password="testpassword123",
        )

    @unittest.mock.patch("requests.get")
    def test_create_invitation_success(self, mock_get):
        import unittest.mock

        # Mock Auth Lookup Response
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": str(self.target_user.id),
            "email": self.target_user.email,
            "username": self.target_user.username,
            "first_name": self.target_user.first_name,
            "last_name": self.target_user.last_name,
        }
        mock_get.return_value = mock_response

        url = reverse(
            "project-invitation-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "invitee_email": "target@example.com",
            "role": ProjectMember.RoleChoices.MEMBER,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["invitee_id"], str(self.target_user.id))
        self.assertEqual(
            response.data["status"], ProjectInvitation.StatusChoices.PENDING
        )

        # Verify DB
        invite = ProjectInvitation.objects.get(id=response.data["id"])
        self.assertEqual(invite.project, self.project)
        self.assertEqual(invite.invited_by, self.owner)

    @unittest.mock.patch("requests.get")
    def test_create_invitation_unauthorized_non_owner(self, mock_get):
        # Authenticate as a regular member
        member_user = User.objects.create_user(
            username="regularmember",
            email="member@example.com",
            password="testpassword123",
        )
        ProjectMember.objects.create(
            project=self.project,
            user=member_user,
            role=ProjectMember.RoleChoices.MEMBER,
            workspace_id=self.workspace_id,
            created_by=self.owner,
        )
        self.client.force_authenticate(user=member_user)

        url = reverse(
            "project-invitation-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": self.project.id},
        )
        data = {
            "invitee_email": "target@example.com",
            "role": ProjectMember.RoleChoices.MEMBER,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @unittest.mock.patch("requests.get")
    def test_accept_invitation_success(self, mock_get):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.ADMIN,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )

        # Authenticate as the target invitee
        self.client.force_authenticate(user=self.target_user)

        url = reverse(
            "project-invitation-accept",
            kwargs={"invitation_id": invite.id},
        )

        response = self.client.post(url, data={"workspace_id": str(self.workspace_id)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"], ProjectInvitation.StatusChoices.ACCEPTED
        )
        self.assertIsNotNone(response.data["accepted_at"])

        # Check ProjectMember creation
        member = ProjectMember.objects.get(project=self.project, user=self.target_user)
        self.assertEqual(member.role, ProjectMember.RoleChoices.ADMIN)

    def test_accept_invitation_forbidden_for_other_user(self):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )

        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=other_user)

        url = reverse(
            "project-invitation-accept",
            kwargs={"invitation_id": invite.id},
        )
        response = self.client.post(url, data={"workspace_id": str(self.workspace_id)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revoke_invitation_success(self):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )

        url = reverse(
            "project-invitation-revoke",
            kwargs={"workspace_id": self.workspace_id, "invitation_id": invite.id},
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"], ProjectInvitation.StatusChoices.REVOKED
        )
        self.assertIsNotNone(response.data["revoked_at"])

    def test_list_pending_invitations_for_user(self):
        # Create invite for target
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )

        self.client.force_authenticate(user=self.target_user)
        url = reverse("user-invitations-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(invite.id))

    def test_user_level_invitation_detail_success(self):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_authenticate(user=self.target_user)
        url = reverse("user-invitation-detail", kwargs={"invitation_id": invite.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(invite.id))

    def test_user_level_invitation_detail_forbidden_for_other_user(self):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        other_user = User.objects.create_user(
            username="otheruser", email="otheruser@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("user-invitation-detail", kwargs={"invitation_id": invite.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_workspace_level_invitation_detail_success_for_owner_admin(self):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_authenticate(user=self.owner)
        url = reverse(
            "workspace-invitation-detail",
            kwargs={"workspace_id": self.workspace_id, "invitation_id": invite.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(invite.id))

    def test_workspace_level_invitation_detail_forbidden_for_member(self):
        invite = ProjectInvitation.objects.create(
            workspace_id=self.workspace_id,
            project=self.project,
            invitee_id=self.target_user.id,
            invitee_email=self.target_user.email,
            role=ProjectMember.RoleChoices.MEMBER,
            status=ProjectInvitation.StatusChoices.PENDING,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        # Authenticate as member of project (not owner/admin)
        member_user = User.objects.create_user(
            username="regularmember",
            email="member@example.com",
            password="testpassword123",
        )
        ProjectMember.objects.create(
            project=self.project,
            user=member_user,
            role=ProjectMember.RoleChoices.MEMBER,
            workspace_id=self.workspace_id,
            created_by=self.owner,
        )
        self.client.force_authenticate(user=member_user)
        url = reverse(
            "workspace-invitation-detail",
            kwargs={"workspace_id": self.workspace_id, "invitation_id": invite.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
