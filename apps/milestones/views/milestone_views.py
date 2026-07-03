from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from milestones.models import Milestone
from milestones.serializers import MilestoneSerializer
from common.permissions import HasWorkspaceProjectAccess
from common.utils.position import shift_positions_on_delete


class MilestoneListCreateAPIView(APIView):
    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]

        # Filtering
        include_archived = (
            request.query_params.get("include_archived", "").lower() == "true"
        )
        milestones = Milestone.objects.filter(project=project)
        if not include_archived:
            milestones = milestones.filter(archived_at__isnull=True)

        status_filter = request.query_params.get("status")
        if status_filter:
            milestones = milestones.filter(status=status_filter)

        # Ordering
        ordering = request.query_params.get("ordering", "position")
        if ordering not in ["position", "-position", "due_date", "-due_date"]:
            ordering = "position"
        milestones = milestones.order_by(ordering)

        serializer = MilestoneSerializer(milestones, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]
        serializer = MilestoneSerializer(
            data=request.data,
            context={"project": project},
        )
        if serializer.is_valid():
            milestone = serializer.save(project=project, created_by=request.user)
            return Response(
                MilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MilestoneDetailAPIView(APIView):
    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, milestone_id):
        milestone = get_object_or_404(
            Milestone,
            pk=milestone_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, milestone)
        serializer = MilestoneSerializer(milestone)
        return Response(serializer.data)

    def patch(self, request, workspace_id, milestone_id):
        milestone = get_object_or_404(
            Milestone,
            pk=milestone_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, milestone)
        serializer = MilestoneSerializer(
            milestone,
            data=request.data,
            partial=True,
            context={"project": milestone.project},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, milestone_id):
        milestone = get_object_or_404(
            Milestone,
            pk=milestone_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, milestone)
        deleted_position = milestone.position
        project = milestone.project
        with transaction.atomic():
            if not milestone.archived_at:
                milestone.archived_at = timezone.now()
                milestone.position = None
                milestone.save()

                queryset = Milestone.objects.filter(project=project)
                shift_positions_on_delete(queryset, deleted_position)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MilestoneReorderAPIView(APIView):
    permission_classes = [HasWorkspaceProjectAccess]

    def patch(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]

        data = request.data
        if not isinstance(data, list):
            return Response(
                {
                    "detail": (
                        "Payload must be a list of objects containing 'id' and"
                        " 'position'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for item in data:
                m_id = item.get("id")
                pos = item.get("position")
                if m_id is None or pos is None:
                    return Response(
                        {"detail": "Each item must have 'id' and 'position'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                milestone = get_object_or_404(
                    Milestone,
                    pk=m_id,
                    project=project,
                    archived_at__isnull=True,
                )
                milestone.position = pos
                milestone.save()

        return Response({"status": "success"}, status=status.HTTP_200_OK)
