import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from projects.models import Project, ProjectMember

User = get_user_model()

class ProjectModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testowner",
            email="testowner@example.com",
            password="testpassword123"
        )
        self.workspace_id = uuid.uuid4()

    def test_project_creation_automatically_adds_owner_member(self):
        # Create project
        project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Test Project",
            code="TEST_PROJ",
            description="Testing project creation member hook."
        )

        # Check if project member was automatically created
        member = ProjectMember.objects.filter(project=project, user=self.user).first()
        self.assertIsNotNone(member)
        self.assertEqual(member.role, ProjectMember.RoleChoices.OWNER)
        self.assertEqual(member.workspace_id, self.workspace_id)
        self.assertEqual(member.created_by, self.user)

    def test_project_save_existing_does_not_duplicate_member(self):
        # Create project
        project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Test Project 2",
            code="TEST_PROJ2"
        )

        # Count active members
        initial_member_count = ProjectMember.objects.filter(project=project).count()
        self.assertEqual(initial_member_count, 1)

        # Update and save project again
        project.description = "Updated description"
        project.save()

        # Check member count remains 1
        self.assertEqual(ProjectMember.objects.filter(project=project).count(), 1)


class ProjectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser",
            email="apiuser@example.com",
            password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_id = uuid.uuid4()

    def test_create_project_api(self):
        url = reverse('project-list-create', kwargs={'workspace_id': self.workspace_id})
        data = {
            'name': 'API Project',
            'code': 'API_PROJ',
            'description': 'Created via API'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify database fields and hook
        project = Project.objects.get(id=response.data['id'])
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
            code="PROJ1"
        )
        # Create a project in a different workspace
        Project.objects.create(
            workspace_id=uuid.uuid4(),
            created_by=self.user,
            name="Project 2",
            code="PROJ2"
        )
        
        url = reverse('project-list-create', kwargs={'workspace_id': self.workspace_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'PROJ1')

    def test_detail_update_delete_project_api(self):
        project = Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Original Project",
            code="ORIG"
        )
        
        detail_url = reverse('project-detail', kwargs={'workspace_id': self.workspace_id, 'pk': project.id})
        
        # Get
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Original Project')
        
        # Patch
        response = self.client.patch(detail_url, {'name': 'Updated Project'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Project')
        
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
            code="ALPHA"
        )
        other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword123"
        )
        
        # Create member via ORM
        member = ProjectMember.objects.create(
            project=project,
            user=other_user,
            role=ProjectMember.RoleChoices.MEMBER,
            workspace_id=self.workspace_id,
            created_by=self.user
        )
        
        members_url = reverse('project-member-list-create', kwargs={
            'workspace_id': self.workspace_id,
            'project_id': project.id
        })
        
        # List members (should have owner + new member)
        response = self.client.get(members_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Remove member (Soft Delete)
        detail_url = reverse('project-member-detail', kwargs={
            'workspace_id': self.workspace_id,
            'project_id': project.id,
            'pk': member.id
        })
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify removed
        response = self.client.get(members_url)
        self.assertEqual(len(response.data), 1) # Only owner remains

    def test_create_project_duplicate_code_validation(self):
        # Create initial project
        Project.objects.create(
            workspace_id=self.workspace_id,
            created_by=self.user,
            name="Project 1",
            code="DUP_CODE"
        )
        
        # Try to create project with same code in same workspace
        url = reverse('project-list-create', kwargs={'workspace_id': self.workspace_id})
        data = {
            'name': 'Project 2',
            'code': 'DUP_CODE'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
        self.assertEqual(
            response.data['code'][0],
            'A project with this code already exists in this workspace.'
        )
