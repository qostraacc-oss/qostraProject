from django.db.models import Max, F
from rest_framework import serializers


def validate_position(queryset, position, instance=None, is_create=True):
    """
    Validates position constraints:
    - On update: Blocks direct modifications to position.
    - On create: Ensures position does not exceed next contiguous index,
      and defaults to next index if not provided.
    """
    if not is_create and instance is not None:
        if position is not None and instance.position != position:
            raise serializers.ValidationError(
                {
                    "position": (
                        "Position cannot be modified directly. Use the reorder"
                        " or move endpoint instead."
                    )
                }
            )
        return instance.position if position is None else position

    if is_create:
        active_qs = queryset
        if hasattr(queryset.model, "archived_at"):
            active_qs = active_qs.filter(archived_at__isnull=True)

        max_pos = active_qs.aggregate(max_pos=Max("position"))["max_pos"]
        next_pos = 0 if max_pos is None else max_pos + 1

        if position is None:
            return next_pos

        if position > next_pos:
            raise serializers.ValidationError(
                {
                    "position": (
                        f"Position cannot exceed the next available sequence"
                        f" index ({next_pos})."
                    )
                }
            )

        return position

    return position


def shift_positions_on_create(queryset, position):
    """
    Shifts all positions >= position up by 1 to make room for insertion.
    Should be called inside transaction.atomic() in serializer create().
    """
    if position is not None:
        active_qs = queryset
        if hasattr(queryset.model, "archived_at"):
            active_qs = active_qs.filter(archived_at__isnull=True)

        active_qs.filter(position__gte=position).update(position=F("position") + 1)


def shift_positions_on_delete(queryset, position):
    """
    Shifts all positions > position down by 1 to fill the gap after deletion/archiving.
    Should be called inside transaction.atomic().
    """
    if position is not None:
        active_qs = queryset
        if hasattr(queryset.model, "archived_at"):
            active_qs = active_qs.filter(archived_at__isnull=True)

        active_qs.filter(position__gt=position).update(position=F("position") - 1)
