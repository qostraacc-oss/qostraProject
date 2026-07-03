from rest_framework import serializers
from tasks.models import Column
from django.db import transaction
from common.utils.position import validate_position, shift_positions_on_create


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

        position = attrs.get("position")
        if board:
            attrs["position"] = validate_position(
                queryset=Column.objects.filter(board=board),
                position=position,
                instance=self.instance,
                is_create=(self.instance is None),
            )

        return attrs

    def create(self, validated_data):
        board = validated_data.get("board")
        position = validated_data.get("position")

        with transaction.atomic():
            queryset = Column.objects.filter(board=board)
            shift_positions_on_create(queryset, position)
            return super().create(validated_data)
