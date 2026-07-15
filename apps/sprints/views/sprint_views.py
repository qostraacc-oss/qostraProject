from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from sprints.models import Sprint
from sprints.serializers import SprintSerializer
from common.permissions import HasWorkspaceProjectAccess


class SprintListCreateAPIView(APIView):
    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]

        sprints = Sprint.objects.filter(project=project)
        status_filter = request.query_params.get("status")
        if status_filter:
            sprints = sprints.filter(status=status_filter)

        serializer = SprintSerializer(sprints, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]
        serializer = SprintSerializer(
            data=request.data,
            context={"project": project},
        )
        if serializer.is_valid():
            sprint = serializer.save(project=project)
            return Response(
                SprintSerializer(sprint).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SprintDetailAPIView(APIView):
    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, sprint_id):
        sprint = get_object_or_404(
            Sprint,
            pk=sprint_id,
        )
        self.check_object_permissions(request, sprint)
        serializer = SprintSerializer(sprint)
        return Response(serializer.data)

    def patch(self, request, workspace_id, sprint_id):
        sprint = get_object_or_404(
            Sprint,
            pk=sprint_id,
        )
        self.check_object_permissions(request, sprint)
        serializer = SprintSerializer(
            sprint,
            data=request.data,
            partial=True,
            context={"project": sprint.project},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, sprint_id):
        sprint = get_object_or_404(
            Sprint,
            pk=sprint_id,
        )
        self.check_object_permissions(request, sprint)
        sprint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
