from rest_framework import serializers
from projects.models import ProjectInvitation, ProjectMember
from common.utils.auth_service import lookup_user_by_email


class ProjectInvitationSerializer(serializers.ModelSerializer):
    invited_by_username = serializers.CharField(
        source="invited_by.username", read_only=True
    )
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_code = serializers.CharField(source="project.code", read_only=True)

    class Meta:
        model = ProjectInvitation
        fields = [
            "id",
            "workspace_id",
            "project",
            "project_name",
            "project_code",
            "invitee_id",
            "invitee_email",
            "role",
            "status",
            "token",
            "invited_by",
            "invited_by_username",
            "created_at",
            "expires_at",
            "accepted_at",
            "declined_at",
            "revoked_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "workspace_id",
            "project",
            "invitee_id",
            "status",
            "token",
            "invited_by",
            "created_at",
            "expires_at",
            "accepted_at",
            "declined_at",
            "revoked_at",
            "updated_at",
        ]

    def validate(self, attrs):
        # Retrieve context parameters
        project = self.context.get("project")
        workspace_id = self.context.get("workspace_id")
        request = self.context.get("request")

        email = attrs.get("invitee_email")

        if not project or not workspace_id:
            raise serializers.ValidationError("Project context is required.")

        # 1. Perform Auth service lookup using request's Auth header
        auth_header = request.META.get("HTTP_AUTHORIZATION") if request else None
        user_data = lookup_user_by_email(email, auth_header=auth_header)

        attrs["invitee_id"] = user_data["id"]
        # Normalize email from auth lookup
        attrs["invitee_email"] = user_data["email"]

        # 2. Check if user is already a project member
        if ProjectMember.objects.filter(
            project=project, user_id=user_data["id"], removed_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                {
                    "invitee_email": "This user is already an active member of this project."
                }
            )

        # 3. Check for existing pending invitation
        if ProjectInvitation.objects.filter(
            project=project,
            invitee_email__iexact=user_data["email"],
            status=ProjectInvitation.StatusChoices.PENDING,
        ).exists():
            raise serializers.ValidationError(
                {
                    "invitee_email": "A pending invitation already exists for this user in this project."
                }
            )

        return attrs
