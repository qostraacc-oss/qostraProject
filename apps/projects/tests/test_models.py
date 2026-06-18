import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
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
