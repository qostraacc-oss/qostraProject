from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import Board, Column
from tasks.serializers import ColumnSerializer
from common.permissions import HasWorkspaceProjectAccess
from common.utils.position import shift_positions_on_delete


class ColumnListCreateAPIView(APIView):
    """
    List and Create columns under a specific board.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, board_id):
        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, board)

        columns = Column.objects.filter(board=board)
        serializer = ColumnSerializer(columns, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, board_id):
        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, board)

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

    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, column_id):
        column = get_object_or_404(
            Column,
            pk=column_id,
            board__project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, column)

        serializer = ColumnSerializer(column)
        return Response(serializer.data)

    def patch(self, request, workspace_id, column_id):
        column = get_object_or_404(
            Column,
            pk=column_id,
            board__project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, column)

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
        column = get_object_or_404(
            Column,
            pk=column_id,
            board__project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, column)

        from django.db import transaction

        deleted_position = column.position
        board = column.board

        with transaction.atomic():
            column.delete()
            queryset = Column.objects.filter(board=board)
            shift_positions_on_delete(queryset, deleted_position)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ColumnReorderAPIView(APIView):
    """
    Reorder all columns for a specific board.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    def patch(self, request, workspace_id, board_id):
        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, board)

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
