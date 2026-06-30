from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from projects.models import ProjectMember
from projects.serializers import ProjectMemberSerializer
from common.permissions import HasWorkspaceProjectAccess


class ProjectMemberListAPIView(APIView):
    """
    List members under a specific project.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, project_id):
        # Access already verified by permission class
        project = request._workspace_project_member_cache["project"]
        members = ProjectMember.objects.filter(project=project, removed_at__isnull=True)
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)


class ProjectMemberDetailAPIView(APIView):
    """
    Retrieve and remove a project member.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    # Custom config: delete operations restricted to owners and admins
    delete_roles = ["owner", "admin"]

    def get(self, request, workspace_id, project_id, pk):
        member = get_object_or_404(
            ProjectMember,
            project_id=project_id,
            pk=pk,
            removed_at__isnull=True,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, member)

        serializer = ProjectMemberSerializer(member)
        return Response(serializer.data)

    def delete(self, request, workspace_id, project_id, pk):
        member = get_object_or_404(
            ProjectMember,
            project_id=project_id,
            pk=pk,
            removed_at__isnull=True,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, member)

        member.removed_at = timezone.now()
        member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
