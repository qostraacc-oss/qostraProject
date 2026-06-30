from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import Board
from tasks.serializers import BoardSerializer
from common.permissions import HasWorkspaceProjectAccess


class BoardListCreateAPIView(APIView):
    """
    List and Create boards under a specific project.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, project_id):
        # Retrieve project from cache created by the permission check
        project = request._workspace_project_member_cache["project"]
        boards = Board.objects.filter(project=project)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]

        serializer = BoardSerializer(
            data=request.data,
            context={"project": project},
        )
        if serializer.is_valid():
            board = serializer.save(project=project)
            return Response(BoardSerializer(board).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailAPIView(APIView):
    """
    Retrieve, update, and delete a board.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    def get(self, request, workspace_id, board_id):
        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, board)

        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def patch(self, request, workspace_id, board_id):
        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, board)

        serializer = BoardSerializer(
            board,
            data=request.data,
            partial=True,
            context={"project": board.project},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, workspace_id, board_id):
        board = get_object_or_404(
            Board,
            pk=board_id,
            project__archived_at__isnull=True,
        )
        self.check_object_permissions(request, board)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
