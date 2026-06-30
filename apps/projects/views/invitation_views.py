from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from projects.models import ProjectInvitation, ProjectMember
from projects.serializers import ProjectInvitationSerializer
from common.permissions import HasWorkspaceProjectAccess


class ProjectInvitationListCreateAPIView(APIView):
    """
    List and Create invitations for a specific project.
    Only project Owners/Admins can invite.
    Project members can list invitations.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    # Members can view/list invitations, but only owners/admins can create them
    read_roles = ["owner", "admin", "member", "viewer"]
    write_roles = ["owner", "admin"]

    def get(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]
        invitations = ProjectInvitation.objects.filter(project=project)
        serializer = ProjectInvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id, project_id):
        project = request._workspace_project_member_cache["project"]

        serializer = ProjectInvitationSerializer(
            data=request.data,
            context={
                "request": request,
                "project": project,
                "workspace_id": workspace_id,
            },
        )
        if serializer.is_valid():
            invitation = serializer.save(
                project=project, workspace_id=workspace_id, invited_by=request.user
            )
            return Response(
                ProjectInvitationSerializer(invitation).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendInvitationAPIView(APIView):
    """
    Resends a pending project invitation (renews expires_at).
    """

    permission_classes = [HasWorkspaceProjectAccess]

    # Custom config: Only owners and admins can write/resend
    write_roles = ["owner", "admin"]

    def post(self, request, workspace_id, invitation_id):
        invitation = get_object_or_404(
            ProjectInvitation, workspace_id=workspace_id, pk=invitation_id
        )
        self.check_object_permissions(request, invitation)

        if invitation.status not in [
            ProjectInvitation.StatusChoices.PENDING,
            ProjectInvitation.StatusChoices.EXPIRED,
        ]:
            return Response(
                {
                    "detail": f"Cannot resend an invitation in status: {invitation.status}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = ProjectInvitation.StatusChoices.PENDING
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.save()

        return Response(ProjectInvitationSerializer(invitation).data)


class RevokeInvitationAPIView(APIView):
    """
    Revokes/cancels a pending invitation.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    # Custom config: Only owners and admins can revoke
    write_roles = ["owner", "admin"]

    def post(self, request, workspace_id, invitation_id):
        invitation = get_object_or_404(
            ProjectInvitation, workspace_id=workspace_id, pk=invitation_id
        )
        self.check_object_permissions(request, invitation)

        if invitation.status != ProjectInvitation.StatusChoices.PENDING:
            return Response(
                {"detail": "Only pending invitations can be revoked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = ProjectInvitation.StatusChoices.REVOKED
        invitation.revoked_at = timezone.now()
        invitation.save()

        return Response(ProjectInvitationSerializer(invitation).data)


class UserPendingInvitationsAPIView(APIView):
    """
    Lists pending invitations for the logged-in user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Auto-expire any pending invitations that have passed their expires_at
        now = timezone.now()
        ProjectInvitation.objects.filter(
            invitee_id=request.user.id,
            status=ProjectInvitation.StatusChoices.PENDING,
            expires_at__lt=now,
        ).update(status=ProjectInvitation.StatusChoices.EXPIRED)

        invitations = ProjectInvitation.objects.filter(
            invitee_id=request.user.id, status=ProjectInvitation.StatusChoices.PENDING
        )
        serializer = ProjectInvitationSerializer(invitations, many=True)
        return Response(serializer.data)


class InvitationDetailAPIView(APIView):
    """
    View details of an invitation by the invitee. Required for acceptance screens.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, invitation_id):
        invitation = get_object_or_404(ProjectInvitation, pk=invitation_id)

        # Enforce that only the target user can view details here
        if invitation.invitee_id != request.user.id:
            return Response(
                {"detail": "You do not have permission to view this invitation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(ProjectInvitationSerializer(invitation).data)


class WorkspaceInvitationDetailAPIView(APIView):
    """
    View details of an invitation by project Owners/Admins within a workspace.
    """

    permission_classes = [HasWorkspaceProjectAccess]

    # Custom config: Only owners and admins can view workspace invitations
    read_roles = ["owner", "admin"]

    def get(self, request, workspace_id, invitation_id):
        invitation = get_object_or_404(
            ProjectInvitation, workspace_id=workspace_id, pk=invitation_id
        )
        self.check_object_permissions(request, invitation)

        return Response(ProjectInvitationSerializer(invitation).data)


class AcceptInvitationAPIView(APIView):
    """
    Accept a pending invitation.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(ProjectInvitation, pk=invitation_id)

        # 1. Enforce that only the target user can accept it
        if invitation.invitee_id != request.user.id:
            return Response(
                {"detail": "This invitation was sent to a different user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 2. Check if already expired
        if invitation.is_expired():
            invitation.status = ProjectInvitation.StatusChoices.EXPIRED
            invitation.save()

        if invitation.status != ProjectInvitation.StatusChoices.PENDING:
            return Response(
                {
                    "detail": f"This invitation is not pending (status: {invitation.status})."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        selected_workspace_id = request.data.get("workspace_id")
        if not selected_workspace_id:
            return Response(
                {"workspace_id": "This field is required on acceptance."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Accept invitation
        invitation.status = ProjectInvitation.StatusChoices.ACCEPTED
        invitation.accepted_at = timezone.now()
        invitation.save()

        # 4. Create or Reactivate Project Member
        member, created = ProjectMember.objects.get_or_create(
            project=invitation.project,
            user=request.user,
            defaults={
                "workspace_id": selected_workspace_id,
                "role": invitation.role,
                "created_by": invitation.invited_by,
            },
        )
        if not created:
            member.removed_at = None
            member.workspace_id = selected_workspace_id
            member.role = invitation.role
            member.created_by = invitation.invited_by
            member.save()

        return Response(ProjectInvitationSerializer(invitation).data)


class DeclineInvitationAPIView(APIView):
    """
    Decline a pending invitation.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(ProjectInvitation, pk=invitation_id)

        if invitation.invitee_id != request.user.id:
            return Response(
                {"detail": "This invitation was sent to a different user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if invitation.is_expired():
            invitation.status = ProjectInvitation.StatusChoices.EXPIRED
            invitation.save()

        if invitation.status != ProjectInvitation.StatusChoices.PENDING:
            return Response(
                {
                    "detail": f"This invitation is not pending (status: {invitation.status})."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = ProjectInvitation.StatusChoices.DECLINED
        invitation.declined_at = timezone.now()
        invitation.save()

        return Response(ProjectInvitationSerializer(invitation).data)
