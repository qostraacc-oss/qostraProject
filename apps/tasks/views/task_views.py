from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from tasks.models import Task, Column
from tasks.serializers import TaskSerializer
from common.permissions import HasWorkspaceProjectAccess
from common.utils.position import shift_positions_on_delete


def check_task_assignment_permission(request, task):
    member_cache = getattr(request, "_workspace_project_member_cache", {})
    is_creator = member_cache.get("is_creator", False)
    member = member_cache.get("member")

    if not is_creator and (not member or member.role not in ["owner", "admin"]):
        if task.assignee != request.user:
            raise PermissionDenied(
                "You do not have permission to access or modify this task because you are not the assignee."
            )


class TaskListCreateAPIView(APIView):
    """
    List and Create Tasks under a specific Project.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    # Creators are allowed by default; define allowed roles for members
    read_roles = ["owner", "admin", "member", "viewer"]
    write_roles = ["owner", "admin", "member"]

    def get(self, request, workspace_id, project_id):
        # Access is checked by permission_classes checking project_id in URL
        tasks = (
            Task.objects.filter(project_id=project_id)
            .select_related("assignee", "reporter", "milestone")
            .prefetch_related("watchers")
        )

        # Enforce role-based visibility: members/viewers only see tasks assigned to themselves
        member_cache = getattr(request, "_workspace_project_member_cache", {})
        is_creator = member_cache.get("is_creator", False)
        member = member_cache.get("member")

        if not is_creator and (not member or member.role not in ["owner", "admin"]):
            tasks = tasks.filter(assignee=request.user)

        # Support filtering by column or assignee
        column_id = request.query_params.get("column_id")
        if column_id:
            tasks = tasks.filter(column_id=column_id)

        assignee_id = request.query_params.get("assignee_id")
        if assignee_id:
            tasks = tasks.filter(assignee_id=assignee_id)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id):
        # Retrieve project from permissions cache or db
        project = request._workspace_project_member_cache["project"]

        serializer = TaskSerializer(
            data=request.data,
            context={"project": project},
        )
        if serializer.is_valid():
            task = serializer.save(project=project, reporter=request.user)
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    """
    Retrieve, update, and delete a Task.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    read_roles = ["owner", "admin", "member", "viewer"]
    write_roles = ["owner", "admin", "member"]
    delete_roles = ["owner", "admin", "member"]

    def get(self, request, workspace_id, task_id):
        task = get_object_or_404(
            Task.objects.select_related("project", "column"),
            pk=task_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, task)
        check_task_assignment_permission(request, task)

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def patch(self, request, workspace_id, task_id):
        task = get_object_or_404(
            Task.objects.select_related("project", "column"),
            pk=task_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, task)
        check_task_assignment_permission(request, task)

        serializer = TaskSerializer(
            task,
            data=request.data,
            partial=True,
            context={"project": task.project},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, task_id):
        task = get_object_or_404(
            Task.objects.select_related("project", "column"),
            pk=task_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, task)
        check_task_assignment_permission(request, task)

        deleted_position = task.position
        column = task.column

        with transaction.atomic():
            task.delete()
            queryset = Task.objects.filter(column=column)
            shift_positions_on_delete(queryset, deleted_position)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskMoveAPIView(APIView):
    """
    Move a task within a column, or to a different column on the same project board.
    """

    permission_classes = [HasWorkspaceProjectAccess]
    write_roles = ["owner", "admin", "member"]

    def patch(self, request, workspace_id, task_id):
        task = get_object_or_404(
            Task.objects.select_related("project", "column"),
            pk=task_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, task)
        check_task_assignment_permission(request, task)

        target_column_id = request.data.get("target_column_id")
        target_position = request.data.get("target_position")

        if target_column_id is None or target_position is None:
            return Response(
                {"error": "Both target_column_id and target_position are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Fetch and validate target column
        target_column = get_object_or_404(
            Column.objects.select_related("board"),
            pk=target_column_id,
            board__project=task.project,
        )

        try:
            target_position = int(target_position)
            if target_position < 0:
                raise ValueError()
        except ValueError:
            return Response(
                {"target_position": "Position must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        source_column = task.column
        source_position = task.position

        # Clamp target position to the max available slot
        max_pos = Task.objects.filter(column=target_column).aggregate(
            models.Max("position")
        )["position__max"]

        # If moving to a different column, max slot is max_pos + 1
        # If moving within same column, max slot is max_pos
        if source_column == target_column:
            limit = 0 if max_pos is None else max_pos
        else:
            limit = 0 if max_pos is None else max_pos + 1

        if target_position > limit:
            target_position = limit

        with transaction.atomic():
            if source_column == target_column:
                if source_position == target_position:
                    # No-op
                    pass
                elif source_position < target_position:
                    # Shift elements between source and target down by 1
                    Task.objects.filter(
                        column=source_column,
                        position__gt=source_position,
                        position__lte=target_position,
                    ).update(position=models.F("position") - 1)
                else:
                    # Shift elements between target and source up by 1
                    Task.objects.filter(
                        column=source_column,
                        position__gte=target_position,
                        position__lt=source_position,
                    ).update(position=models.F("position") + 1)

                # Update task position
                Task.objects.filter(pk=task_id).update(position=target_position)
            else:
                # 1. Decrement positions in source column for tasks after the moved task
                Task.objects.filter(
                    column=source_column,
                    position__gt=source_position,
                ).update(position=models.F("position") - 1)

                # 2. Increment positions in target column for tasks at or after target position
                Task.objects.filter(
                    column=target_column,
                    position__gte=target_position,
                ).update(position=models.F("position") + 1)

                # 3. Update task itself
                Task.objects.filter(pk=task_id).update(
                    column=target_column,
                    position=target_position,
                )

        # Fetch updated task representation
        task.refresh_from_db()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
