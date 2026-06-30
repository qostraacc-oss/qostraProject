from rest_framework import serializers
from django.db import models, transaction
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "number",
            "type",
            "column",
            "status",
            "position",
            "title",
            "description",
            "priority",
            "estimate",
            "time_spent",
            "reporter",
            "assignee",
            "watchers",
            "start_date",
            "due_date",
            "completed_at",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "number",
            "reporter",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        project = self.context.get("project") or (
            self.instance.project if self.instance else None
        )
        column = attrs.get("column") or (
            self.instance.column if self.instance else None
        )

        # 1. Verify column belongs to the same project
        if column and project and column.board.project != project:
            raise serializers.ValidationError(
                {
                    "column": "The selected column does not belong to a board in this project."
                }
            )

        # 2. Verify assignee and watchers are members of the project
        if project:
            active_member_ids = project.active_member_ids

            assignee = attrs.get("assignee")
            if assignee and assignee.id not in active_member_ids:
                raise serializers.ValidationError(
                    {
                        "assignee": "The assignee must be an active member of this project."
                    }
                )

            watchers = attrs.get("watchers")
            if watchers:
                for watcher in watchers:
                    if watcher.id not in active_member_ids:
                        raise serializers.ValidationError(
                            {
                                "watchers": "All watchers must be active members of this project."
                            }
                        )

        # 4. Verify dates
        start_date = attrs.get("start_date") or (
            self.instance.start_date if self.instance else None
        )
        due_date = attrs.get("due_date") or (
            self.instance.due_date if self.instance else None
        )
        if start_date and due_date and start_date > due_date:
            raise serializers.ValidationError(
                {"due_date": "Due date must be after start date."}
            )

        # 5. Prevent direct updates to position and column via standard serializer save
        if self.instance:
            if "position" in attrs:
                raise serializers.ValidationError(
                    {
                        "position": "Position cannot be modified directly. Use the move endpoint instead."
                    }
                )
            if "column" in attrs:
                raise serializers.ValidationError(
                    {
                        "column": "Column cannot be modified directly. Use the move endpoint instead."
                    }
                )

        # 6. Auto-calculate position on creation
        if not self.instance and attrs.get("position") is None and column:
            max_pos = Task.objects.filter(column=column).aggregate(
                models.Max("position")
            )["position__max"]
            attrs["position"] = 0 if max_pos is None else max_pos + 1

        return attrs

    def create(self, validated_data):
        column = validated_data.get("column")
        position = validated_data.get("position", 0)

        with transaction.atomic():
            # Shift all tasks in the column >= position up by 1
            Task.objects.filter(column=column, position__gte=position).update(
                position=models.F("position") + 1
            )
            return super().create(validated_data)
