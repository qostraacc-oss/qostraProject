from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from projects.models import Project, ProjectMember
from projects.serializers import ProjectMemberSerializer


class ProjectMemberListAPIView(APIView):
    """
    List members under a specific project.
    """

    def get(self, request, workspace_id, project_id):
        # Ensure project exists and is active in the workspace
        project = get_object_or_404(
            Project.objects.for_workspace(workspace_id, request.user),
            pk=project_id,
            archived_at__isnull=True
        )
        members = ProjectMember.objects.filter(project=project, removed_at__isnull=True)
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)


class ProjectMemberDetailAPIView(APIView):
    """
    Retrieve and remove a project member.
    """

    def get_object(self, workspace_id, project_id, pk, user):
        project = get_object_or_404(
            Project.objects.for_workspace(workspace_id, user),
            pk=project_id,
            archived_at__isnull=True
        )
        return get_object_or_404(
            ProjectMember,
            project=project,
            pk=pk,
            removed_at__isnull=True,
        )

    def get(self, request, workspace_id, project_id, pk):
        member = self.get_object(workspace_id, project_id, pk, request.user)
        serializer = ProjectMemberSerializer(member)
        return Response(serializer.data)

    def delete(self, request, workspace_id, project_id, pk):
        member = self.get_object(workspace_id, project_id, pk, request.user)
        member.removed_at = timezone.now()
        member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
