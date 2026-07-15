from rest_framework import serializers
from labels.models import Label
from common.utils.position import validate_position


class LabelSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(required=False)
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = Label
        fields = [
            "id",
            "workspace_id",
            "project",
            "name",
            "slug",
            "color",
            "description",
            "position",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "workspace_id",
            "slug",
            "is_archived",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        workspace_id = self.context.get("workspace_id")
        project = attrs.get("project") or (
            self.instance.project if self.instance else None
        )

        name = attrs.get("name") or (self.instance.name if self.instance else None)

        if workspace_id and name:
            query = Label.objects.filter(
                workspace_id=workspace_id,
                project=project,
                name=name,
                is_archived=False,
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {"name": "A label with this name already exists in this scope."}
                )

        position = attrs.get("position")
        if workspace_id:
            queryset = Label.objects.filter(
                workspace_id=workspace_id, project=project, is_archived=False
            )
            attrs["position"] = validate_position(
                queryset=queryset,
                position=position,
                instance=self.instance,
                is_create=(self.instance is None),
            )

        return attrs
