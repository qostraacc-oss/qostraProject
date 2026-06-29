from rest_framework import serializers
from tasks.models import Column
from django.db import models, transaction


class ColumnSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(required=False)

    class Meta:
        model = Column
        fields = [
            "id",
            "board",
            "name",
            "position",
            "category",
            "color",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "board",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        board = self.context.get("board") or (
            self.instance.board if self.instance else None
        )
        name = attrs.get("name") or (self.instance.name if self.instance else None)

        if board and name:
            query = Column.objects.filter(board=board, name=name)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {"name": "A column with this name already exists on this board."}
                )

        if self.instance and "position" in attrs:
            raise serializers.ValidationError(
                {
                    "position": "Position cannot be modified directly. Use the bulk reorder endpoint instead."
                }
            )

        if "position" not in attrs and not self.instance and board:
            max_pos = Column.objects.filter(board=board).aggregate(
                models.Max("position")
            )["position__max"]
            attrs["position"] = 0 if max_pos is None else max_pos + 1

        return attrs

    def create(self, validated_data):
        board = validated_data.get("board")
        position = validated_data.get("position")

        with transaction.atomic():
            # Shift all columns >= position up by 1
            Column.objects.filter(board=board, position__gte=position).update(
                position=models.F("position") + 1
            )
            return super().create(validated_data)
