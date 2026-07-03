from rest_framework import serializers
from milestones.models import Milestone
from common.utils.position import validate_position, shift_positions_on_create


class MilestoneSerializer(serializers.ModelSerializer):
    progress = serializers.FloatField(read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    completed_task_count = serializers.IntegerField(read_only=True)
    overdue_task_count = serializers.IntegerField(read_only=True)
    is_archived = serializers.BooleanField(read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Milestone
        fields = [
            "id",
            "project",
            "name",
            "description",
            "start_date",
            "due_date",
            "completed_at",
            "status",
            "position",
            "color",
            "archived_at",
            "is_archived",
            "created_by",
            "created_by_username",
            "progress",
            "task_count",
            "completed_task_count",
            "overdue_task_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "completed_at",
            "archived_at",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
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

        project = self.context.get("project") or (
            self.instance.project if self.instance else None
        )

        position = attrs.get("position")
        if project:
            attrs["position"] = validate_position(
                queryset=Milestone.objects.filter(project=project),
                position=position,
                instance=self.instance,
                is_create=(self.instance is None),
            )

        name = attrs.get("name")
        if name and project:
            query = Milestone.objects.filter(
                project=project, name=name, archived_at__isnull=True
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {
                        "name": (
                            "A milestone with this name already exists in this project."
                        )
                    }
                )

        return attrs

    def create(self, validated_data):
        project = validated_data.get("project")
        position = validated_data.get("position")

        from django.db import transaction

        with transaction.atomic():
            queryset = Milestone.objects.filter(project=project)
            shift_positions_on_create(queryset, position)
            return super().create(validated_data)
