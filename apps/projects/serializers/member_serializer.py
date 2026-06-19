from rest_framework import serializers
from projects.models import ProjectMember
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id",
            "workspace_id",
            "project",
            "user",
            "user_email",
            "user_username",
            "role",
            "created_by",
            "removed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "workspace_id",
            "project",
            "created_by",
            "removed_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        project = self.context.get("project") or attrs.get("project")
        user = attrs.get("user")

        if project and user:
            query = ProjectMember.objects.filter(
                project=project, user=user, removed_at__isnull=True
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": "This user is already an active member of this project."
                    }
                )
        return attrs
