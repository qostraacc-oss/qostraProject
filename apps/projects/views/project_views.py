from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from projects.models import Project
from projects.serializers import ProjectSerializer
from common.permissions import HasWorkspaceProjectAccess


class ProjectListCreateAPIView(APIView):
    """
    List and Create projects under a specific workspace.
    """

    def get(self, request, workspace_id):
        # Filter projects by workspace mapping
        projects = Project.objects.for_workspace(workspace_id, request.user).filter(
            archived_at__isnull=True
        )

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id):
        serializer = ProjectSerializer(
            data=request.data,
            context={"request": request, "workspace_id": workspace_id},
        )
        if serializer.is_valid():
            project = serializer.save(
                workspace_id=workspace_id, created_by=request.user
            )
            return Response(
                ProjectSerializer(project).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):
    """
    Retrieve, update, and soft-delete a project.
    """
    permission_classes = [HasWorkspaceProjectAccess]

    # Creators and owners can delete/archive projects. Admins and owners can update/edit.
    delete_roles = ["owner"]

    def get(self, request, workspace_id, pk):
        project = get_object_or_404(Project, pk=pk, archived_at__isnull=True)
        self.check_object_permissions(request, project)
        
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, workspace_id, pk):
        project = get_object_or_404(Project, pk=pk, archived_at__isnull=True)
        self.check_object_permissions(request, project)

        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True,
            context={"request": request, "workspace_id": workspace_id},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, pk):
        project = get_object_or_404(Project, pk=pk, archived_at__isnull=True)
        self.check_object_permissions(request, project)

        project.archived_at = timezone.now()
        project.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
