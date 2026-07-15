from rest_framework import serializers
from decimal import Decimal
from timelogs.models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = TimeLog
        fields = [
            "id",
            "task",
            "user",
            "username",
            "duration",
            "description",
            "logged_at",
            "is_locked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task",
            "user",
            "is_locked",
            "created_at",
            "updated_at",
        ]

    def validate_duration(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Duration must be a positive number.")
        return value
