from rest_framework import serializers
from sprints.models import Sprint


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = [
            "id",
            "project",
            "name",
            "goal",
            "status",
            "start_date",
            "end_date",
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
        start_date = attrs.get("start_date") or (
            self.instance.start_date if self.instance else None
        )
        end_date = attrs.get("end_date") or (
            self.instance.end_date if self.instance else None
        )
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        project = self.context.get("project") or (
            self.instance.project if self.instance else None
        )

        name = attrs.get("name")
        if name and project:
            query = Sprint.objects.filter(project=project, name=name)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {
                        "name": (
                            "A sprint with this name already exists in this project."
                        )
                    }
                )

        return attrs
