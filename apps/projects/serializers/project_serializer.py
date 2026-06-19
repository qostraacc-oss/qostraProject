from rest_framework import serializers
from projects.models import Project
from projects.serializers.member_serializer import ProjectMemberSerializer


class ProjectSerializer(serializers.ModelSerializer):
    members = ProjectMemberSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "workspace_id",
            "client_id",
            "created_by",
            "created_by_username",
            "name",
            "slug",
            "code",
            "description",
            "status",
            "priority",
            "start_date",
            "target_end_date",
            "actual_end_date",
            "archived_at",
            "created_at",
            "updated_at",
            "members",
        ]
        read_only_fields = [
            "id",
            "workspace_id",
            "created_by",
            "slug",
            "archived_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        workspace_id = self.context.get("workspace_id")
        code = attrs.get("code") or (self.instance.code if self.instance else None)

        if workspace_id and code:
            query = Project.objects.filter(workspace_id=workspace_id, code=code)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {
                        "code": "A project with this code already exists in this workspace."
                    }
                )

        # Validate external client_id against Directory service
        client_id = attrs.get("client_id")
        if client_id and workspace_id:
            from common.utils.directory import validate_directory_client

            request = self.context.get("request")
            auth_header = None
            if request:
                auth_header = request.META.get("HTTP_AUTHORIZATION")

            validate_directory_client(
                workspace_id=workspace_id, client_id=client_id, auth_header=auth_header
            )

        return attrs
