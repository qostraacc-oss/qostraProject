from rest_framework import serializers
from django.db import transaction
from common.utils.position import validate_position, shift_positions_on_create
from tasks.models import Task
from labels.models import Label




class TaskMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        from milestones.models import Milestone

        model = Milestone
        fields = ["id", "name", "color", "status"]


class TaskLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name", "color", "slug"]


class TaskSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(required=False)
    milestone_detail = TaskMilestoneSerializer(source="milestone", read_only=True)
    labels = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all(),
        required=False,
    )
    labels_detail = TaskLabelSerializer(source="labels", many=True, read_only=True)

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
            "milestone",
            "milestone_detail",
            "labels",
            "labels_detail",
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

        # 3. Verify milestone alignment
        milestone = attrs.get("milestone") or (
            self.instance.milestone if self.instance else None
        )
        if milestone and project:
            if milestone.project != project:
                raise serializers.ValidationError(
                    {
                        "milestone": "The selected milestone does not belong to this project."
                    }
                )
            if milestone.project.workspace_id != project.workspace_id:
                raise serializers.ValidationError(
                    {"milestone": "The selected milestone is in a different workspace."}
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
            if "column" in attrs:
                raise serializers.ValidationError(
                    {
                        "column": "Column cannot be modified directly. Use the move endpoint instead."
                    }
                )

        position = attrs.get("position")
        if column:
            attrs["position"] = validate_position(
                queryset=Task.objects.filter(column=column),
                position=position,
                instance=self.instance,
                is_create=(self.instance is None),
            )

        # 6. Verify labels are valid for the project & workspace
        labels = attrs.get("labels")
        if labels is not None and project:
            for label in labels:
                if str(label.workspace_id) != str(project.workspace_id):
                    raise serializers.ValidationError(
                        {"labels": f"Label '{label.name}' does not belong to this workspace."}
                    )
                if label.project and label.project != project:
                    raise serializers.ValidationError(
                        {"labels": f"Label '{label.name}' does not belong to this project."}
                    )
                if label.is_archived:
                    raise serializers.ValidationError(
                        {"labels": f"Label '{label.name}' is archived and cannot be assigned."}
                    )

        return attrs


    def create(self, validated_data):
        column = validated_data.get("column")
        position = validated_data.get("position")

        with transaction.atomic():
            queryset = Task.objects.filter(column=column)
            shift_positions_on_create(queryset, position)
            return super().create(validated_data)
