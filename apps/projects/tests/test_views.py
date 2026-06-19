import uuid
import unittest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project, ProjectMember

User = get_user_model()


class ProjectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser", email="apiuser@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

    def test_create_project_api(self):
        url = reverse("project-list-create", kwargs={"workspace_id": self.workspace_id})
        data = {
            "name": "API Project",
            "code": "API_PROJ",
            "description": "Created via API",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify database fields and hook
        project = Project.objects.get(id=response.data["id"])
        self.assertEqual(project.workspace_id, self.workspace_id)
        self.assertEqual(project.created_by, self.user)

        member = ProjectMember.objects.filter(project=project, user=self.user).first()
        self.assertIsNotNone(member)
        self.assertEqual(member.role, ProjectMember.RoleChoices.OWNER)

    def test_list_projects_api(self):
        # Create a project
        Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Project 1",
            code="PROJ1",
        )
        # Create a project in a different workspace
        Project.objects.create(
            workspace_id=uuid.uuid4(),
            created_by=self.user,
            name="Project 2",
            code="PROJ2",
        )

        url = reverse("project-list-create", kwargs={"workspace_id": self.workspace_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["code"], "PROJ1")

    def test_detail_update_delete_project_api(self):
        project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Original Project",
            code="ORIG",
        )

        detail_url = reverse(
            "project-detail",
            kwargs={"workspace_id": self.workspace_id, "pk": project.id},
        )

        # Get
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Original Project")

        # Patch
        response = self.client.patch(
            detail_url, {"name": "Updated Project"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Project")

        # Delete (Soft Delete)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        project.refresh_from_db()
        self.assertIsNotNone(project.archived_at)

    def test_project_members_api(self):
        project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Project Alpha",
            code="ALPHA",
        )
        other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword123",
        )

        # Create member via ORM
        member = ProjectMember.objects.create(
            project=project,
            user=other_user,
            role=ProjectMember.RoleChoices.MEMBER,
            workspace_id=self.workspace_id,
            created_by=self.user,
        )

        members_url = reverse(
            "project-member-list-create",
            kwargs={"workspace_id": self.workspace_id, "project_id": project.id},
        )

        # List members (should have owner + new member)
        response = self.client.get(members_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Remove member (Soft Delete)
        detail_url = reverse(
            "project-member-detail",
            kwargs={
                "workspace_id": self.workspace_id,
                "project_id": project.id,
                "pk": member.id,
            },
        )
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify removed
        response = self.client.get(members_url)
        self.assertEqual(len(response.data), 1)  # Only owner remains

    def test_create_project_duplicate_code_validation(self):
        # Create initial project
        Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Project 1",
            code="DUP_CODE",
        )

        # Try to create project with same code in same workspace
        url = reverse("project-list-create", kwargs={"workspace_id": self.workspace_id})
        data = {"name": "Project 2", "code": "DUP_CODE"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)
        self.assertEqual(
            response.data["code"][0],
            "A project with this code already exists in this workspace.",
        )

    @unittest.mock.patch("requests.get")
    def test_create_project_with_valid_client_id(self, mock_get):
        import unittest.mock

        # Configure mocked response
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client_uuid = uuid.uuid4()
        url = reverse("project-list-create", kwargs={"workspace_id": self.workspace_id})
        data = {
            "name": "API Project with Client",
            "code": "CLIENT_OK",
            "client_id": str(client_uuid),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_get.assert_called_once()

    @unittest.mock.patch("requests.get")
    def test_create_project_with_invalid_client_id(self, mock_get):
        import unittest.mock

        # Configure mocked response for missing client (404)
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client_uuid = uuid.uuid4()
        url = reverse("project-list-create", kwargs={"workspace_id": self.workspace_id})
        data = {
            "name": "API Project with Bad Client",
            "code": "CLIENT_BAD",
            "client_id": str(client_uuid),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client_id", response.data)
        self.assertEqual(
            response.data["client_id"][0],
            "Client does not exist in this workspace or is inactive.",
        )

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "test-projects-cache",
            }
        }
    )
    @unittest.mock.patch("requests.get")
    def test_create_project_directory_validation_caching(self, mock_get):
        import unittest.mock
        from django.core.cache import cache

        # Clear cache before starting
        cache.clear()

        # Configure mocked response
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client_uuid = uuid.uuid4()
        url = reverse("project-list-create", kwargs={"workspace_id": self.workspace_id})

        # 1. First Project Creation (should miss cache and hit external API)
        data1 = {
            "name": "Cached Project 1",
            "code": "CACHE_PROJ1",
            "client_id": str(client_uuid),
        }
        response1 = self.client.post(url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mock_get.call_count, 1)

        # 2. Second Project Creation (should hit cache and not call external API)
        data2 = {
            "name": "Cached Project 2",
            "code": "CACHE_PROJ2",
            "client_id": str(client_uuid),
        }
        response2 = self.client.post(url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mock_get.call_count, 1)  # Still 1 call total
