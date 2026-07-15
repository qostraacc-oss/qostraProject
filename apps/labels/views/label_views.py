from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from labels.models import Label
from labels.serializers import LabelSerializer
from projects.models import Project
from common.permissions import IsWorkspaceMember, IsWorkspaceOrProjectAdmin



class LabelListCreateAPIView(APIView):
    """
    List and Create labels.
    Supports workspace-wide labels and project-scoped labels.
    """

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsWorkspaceMember()]
        return [permissions.IsAuthenticated(), IsWorkspaceOrProjectAdmin()]

    def get(self, request, workspace_id, project_id=None):
        if project_id:
            # Retrieve all available labels for the project:
            # Includes workspace-wide labels AND project-scoped labels
            labels = Label.objects.filter(
                workspace_id=workspace_id, is_archived=False
            ).filter(Q(project__isnull=True) | Q(project_id=project_id))
        else:
            # Retrieve workspace-wide labels only
            labels = Label.objects.filter(
                workspace_id=workspace_id, project__isnull=True, is_archived=False
            )

        serializer = LabelSerializer(labels, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id=None):
        project = None
        if project_id:
            project = get_object_or_404(
                Project, pk=project_id, workspace_id=workspace_id
            )

        serializer = LabelSerializer(
            data=request.data,
            context={"workspace_id": workspace_id, "project": project},
        )
        if serializer.is_valid():
            label = serializer.save(workspace_id=workspace_id, project=project)
            return Response(
                LabelSerializer(label).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LabelDetailAPIView(APIView):
    """
    Retrieve, update, or archive a Label.
    """

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsWorkspaceMember()]
        return [permissions.IsAuthenticated(), IsWorkspaceOrProjectAdmin()]

    def get_object(self, workspace_id, label_id):
        return get_object_or_404(
            Label, pk=label_id, workspace_id=workspace_id, is_archived=False
        )

    def get(self, request, workspace_id, label_id):
        label = self.get_object(workspace_id, label_id)
        if label.project:
            self.check_object_permissions(request, label.project)
        serializer = LabelSerializer(label)
        return Response(serializer.data)

    def patch(self, request, workspace_id, label_id):
        label = self.get_object(workspace_id, label_id)
        if label.project:
            self.check_object_permissions(request, label.project)

        serializer = LabelSerializer(
            label,
            data=request.data,
            partial=True,
            context={"workspace_id": workspace_id, "project": label.project},
        )
        if serializer.is_valid():
            label = serializer.save()
            return Response(LabelSerializer(label).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, label_id):
        label = self.get_object(workspace_id, label_id)
        if label.project:
            self.check_object_permissions(request, label.project)

        label.is_archived = True
        label.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllLabelsListAPIView(APIView):
    """
    List all active labels (both workspace-wide and project-scoped) in a workspace.
    """

    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_id):
        labels = Label.objects.filter(workspace_id=workspace_id, is_archived=False)
        serializer = LabelSerializer(labels, many=True)
        return Response(serializer.data)

