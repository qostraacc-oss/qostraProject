from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from projects.models import Project, ProjectMember
from projects.serializers import ProjectSerializer


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

    def get_object(self, workspace_id, pk, user):
        from django.http import Http404

        project = get_object_or_404(Project, pk=pk, archived_at__isnull=True)

        is_creator = project.created_by == user and project.workspace_id == workspace_id
        member = ProjectMember.objects.filter(
            project=project,
            user=user,
            workspace_id=workspace_id,
            removed_at__isnull=True,
        ).first()

        if not is_creator and not member:
            if project.workspace_id != workspace_id:
                raise Http404("No Project matches the given query.")
            raise PermissionDenied("You do not have permission to access this project.")

        return project

    def get(self, request, workspace_id, pk):
        project = self.get_object(workspace_id, pk, request.user)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, workspace_id, pk):
        project = self.get_object(workspace_id, pk, request.user)

        # Only owners/admins or creator can update project
        is_owner_or_admin = ProjectMember.objects.filter(
            project=project,
            user=request.user,
            role__in=[ProjectMember.RoleChoices.OWNER, ProjectMember.RoleChoices.ADMIN],
            removed_at__isnull=True,
        ).exists()

        if project.created_by != request.user and not is_owner_or_admin:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can update the project."
            )

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
        project = self.get_object(workspace_id, pk, request.user)

        # Only creator or owner can archive/delete project
        is_owner = ProjectMember.objects.filter(
            project=project,
            user=request.user,
            role=ProjectMember.RoleChoices.OWNER,
            removed_at__isnull=True,
        ).exists()

        if project.created_by != request.user and not is_owner:
            raise PermissionDenied(
                "Only the project owner or creator can archive the project."
            )

        project.archived_at = timezone.now()
        project.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
