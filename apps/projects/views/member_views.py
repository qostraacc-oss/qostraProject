from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from projects.models import Project, ProjectMember
from apps.projects.serializers import ProjectMemberSerializer

class ProjectMemberListAPIView(APIView):
    """
    List members under a specific project.
    """
    def get(self, request, workspace_id, project_id):
        # Ensure project exists and is active in the workspace
        project = get_object_or_404(Project, workspace_id=workspace_id, pk=project_id, archived_at__isnull=True)
        members = ProjectMember.objects.filter(project=project, removed_at__isnull=True)
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)


class ProjectMemberDetailAPIView(APIView):
    """
    Retrieve and remove a project member.
    """
    def get_object(self, workspace_id, project_id, pk):
        return get_object_or_404(
            ProjectMember,
            workspace_id=workspace_id,
            project_id=project_id,
            pk=pk,
            removed_at__isnull=True
        )

    def get(self, request, workspace_id, project_id, pk):
        member = self.get_object(workspace_id, project_id, pk)
        serializer = ProjectMemberSerializer(member)
        return Response(serializer.data)

    def delete(self, request, workspace_id, project_id, pk):
        member = self.get_object(workspace_id, project_id, pk)
        member.removed_at = timezone.now()
        member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
