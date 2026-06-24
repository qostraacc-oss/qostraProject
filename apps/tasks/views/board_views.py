from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from projects.models import Project, ProjectMember
from tasks.models import Board
from tasks.serializers import BoardSerializer


class BoardListCreateAPIView(APIView):
    """
    List and Create boards under a specific project.
    """

    def get_project_member(self, workspace_id, project_id, user):
        project = get_object_or_404(
            Project, workspace_id=workspace_id, pk=project_id, archived_at__isnull=True
        )

        member = ProjectMember.objects.filter(
            project=project, user=user, removed_at__isnull=True
        ).first()

        if project.created_by != user and not member:
            raise PermissionDenied("You do not have permission to access this project.")

        return project, member

    def get(self, request, workspace_id, project_id):
        project, member = self.get_project_member(
            workspace_id, project_id, request.user
        )
        boards = Board.objects.filter(project=project)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id):
        project, member = self.get_project_member(
            workspace_id, project_id, request.user
        )

        # Only owners, admins, or project creator can create boards
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can create boards."
            )

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

    def get_board_and_member(self, workspace_id, board_id, user):
        board = get_object_or_404(
            Board,
            project__workspace_id=workspace_id,
            pk=board_id,
            project__archived_at__isnull=True,
        )

        member = ProjectMember.objects.filter(
            project=board.project, user=user, removed_at__isnull=True
        ).first()

        if board.project.created_by != user and not member:
            raise PermissionDenied("You do not have permission to access this project.")

        return board, member

    def get(self, request, workspace_id, board_id):
        board, member = self.get_board_and_member(workspace_id, board_id, request.user)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def patch(self, request, workspace_id, board_id):
        board, member = self.get_board_and_member(workspace_id, board_id, request.user)

        # Only owners, admins, or project creator can edit boards
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if board.project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can update boards."
            )

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
        board, member = self.get_board_and_member(workspace_id, board_id, request.user)

        # Only owners, admins, or project creator can delete boards
        is_admin_or_owner = member and member.role in [
            ProjectMember.RoleChoices.OWNER,
            ProjectMember.RoleChoices.ADMIN,
        ]
        if board.project.created_by != request.user and not is_admin_or_owner:
            raise PermissionDenied(
                "Only project owners, admins, or the creator can delete boards."
            )

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
