from rest_framework import serializers
from tasks.models import Board, Column


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

    def create(self, validated_data):
        board = super().create(validated_data)
        Column.objects.bulk_create(
            [
                Column(
                    board=board,
                    name="To Do",
                    position=0,
                    category=Column.Category.OPEN,
                    color="#9CA3AF",
                ),
                Column(
                    board=board,
                    name="In Progress",
                    position=1,
                    category=Column.Category.OPEN,
                    color="#3B82F6",
                ),
                Column(
                    board=board,
                    name="Done",
                    position=2,
                    category=Column.Category.DONE,
                    color="#10B981",
                ),
            ]
        )
        return board
