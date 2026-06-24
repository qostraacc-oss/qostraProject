from rest_framework import serializers
from tasks.models import Board


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = [
            "id",
            "project",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        project = self.context.get("project") or (
            self.instance.project if self.instance else None
        )
        name = attrs.get("name") or (self.instance.name if self.instance else None)

        if project and name:
            query = Board.objects.filter(project=project, name=name)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {"name": "A board with this name already exists in the project."}
                )

        return attrs
