from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from projects.models import ProjectMember
from tasks.models import Board, Column
from tasks.serializers import ColumnSerializer


class ColumnListCreateAPIView(APIView):
    """
    List and Create columns under a specific board.
    """

    def get_board_and_member(self, workspace_id, board_id, user):
        from django.http import Http404

        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )

        project = board.project
        is_creator = project.created_by == user and project.workspace_id == workspace_id
        member = ProjectMember.objects.filter(
            project=project,
            user=user,
            workspace_id=workspace_id,
            removed_at__isnull=True,
        ).first()

        if not is_creator and not member:
            if project.workspace_id != workspace_id:
                raise Http404("No Board matches the given query.")
            raise PermissionDenied("You do not have permission to access this project.")

        return board, member

    def get(self, request, workspace_id, board_id):
        board, member = self.get_board_and_member(workspace_id, board_id, request.user)
        columns = Column.objects.filter(board=board)
        serializer = ColumnSerializer(columns, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, board_id):
        board, member = self.get_board_and_member(workspace_id, board_id, request.user)

        # Only owners, admins, or project creator can create columns
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if board.project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can create columns."
            )

        serializer = ColumnSerializer(
            data=request.data,
            context={"board": board},
        )
        if serializer.is_valid():
            column = serializer.save(board=board)
            return Response(
                ColumnSerializer(column).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColumnDetailAPIView(APIView):
    """
    Retrieve, update, and delete a column.
    """

    def get_column_and_member(self, workspace_id, column_id, user):
        from django.http import Http404

        column = get_object_or_404(
            Column,
            pk=column_id,
            board__project__archived_at__isnull=True,
        )

        project = column.board.project
        is_creator = project.created_by == user and project.workspace_id == workspace_id
        member = ProjectMember.objects.filter(
            project=project,
            user=user,
            workspace_id=workspace_id,
            removed_at__isnull=True,
        ).first()

        if not is_creator and not member:
            if project.workspace_id != workspace_id:
                raise Http404("No Column matches the given query.")
            raise PermissionDenied("You do not have permission to access this project.")

        return column, member

    def get(self, request, workspace_id, column_id):
        column, member = self.get_column_and_member(
            workspace_id, column_id, request.user
        )
        serializer = ColumnSerializer(column)
        return Response(serializer.data)

    def patch(self, request, workspace_id, column_id):
        column, member = self.get_column_and_member(
            workspace_id, column_id, request.user
        )

        # Only owners, admins, or project creator can edit columns
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if column.board.project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can update columns."
            )

        serializer = ColumnSerializer(
            column,
            data=request.data,
            partial=True,
            context={"board": column.board},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, column_id):
        column, member = self.get_column_and_member(
            workspace_id, column_id, request.user
        )

        # Only owners, admins, or project creator can delete columns
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if column.board.project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can delete columns."
            )

        from django.db import transaction, models

        deleted_position = column.position
        board = column.board

        with transaction.atomic():
            column.delete()
            # Shift remaining columns with position > deleted_position down by 1
            Column.objects.filter(board=board, position__gt=deleted_position).update(
                position=models.F("position") - 1
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ColumnReorderAPIView(APIView):
    """
    Reorder all columns for a specific board.
    """

    def get_board_and_member(self, workspace_id, board_id, user):
        from django.http import Http404

        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )

        project = board.project
        is_creator = project.created_by == user and project.workspace_id == workspace_id
        member = ProjectMember.objects.filter(
            project=project,
            user=user,
            workspace_id=workspace_id,
            removed_at__isnull=True,
        ).first()

        if not is_creator and not member:
            if project.workspace_id != workspace_id:
                raise Http404("No Board matches the given query.")
            raise PermissionDenied("You do not have permission to access this project.")

        return board, member

    def patch(self, request, workspace_id, board_id):
        board, member = self.get_board_and_member(workspace_id, board_id, request.user)

        # Only owners, admins, or project creator can reorder columns
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if board.project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can reorder columns."
            )

        column_ids = request.data.get("column_ids")
        if not column_ids or not isinstance(column_ids, list):
            return Response(
                {"error": "column_ids must be a non-empty list of integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify all provided columns belong to the board
        columns = Column.objects.filter(board=board, id__in=column_ids)
        if columns.count() != len(column_ids):
            return Response(
                {
                    "error": "Some column IDs are invalid or do not belong to this board."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update positions inside a transaction
        from django.db import transaction

        with transaction.atomic():
            for index, col_id in enumerate(column_ids):
                Column.objects.filter(board=board, id=col_id).update(position=index)

        # Return updated list of columns
        updated_columns = Column.objects.filter(board=board).order_by("position")
        serializer = ColumnSerializer(updated_columns, many=True)
        return Response(serializer.data)
