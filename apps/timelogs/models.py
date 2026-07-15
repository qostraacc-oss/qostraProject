import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from common.permissions import WorkspaceResourceMixin


class TimeLog(WorkspaceResourceMixin, models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Connections / Relations
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="timelogs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="timelogs"
    )

    # Log details
    duration = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Duration spent in hours. Must be positive.",
    )
    description = models.TextField(
        blank=True, default="", help_text="Optional description of work performed."
    )
    logged_at = models.DateField(
        default=timezone.now, help_text="The date the work was actually performed."
    )

    # Billing & Lock System
    is_locked = models.BooleanField(
        default=False,
        help_text="Once locked (billing finalized), the log cannot be edited or deleted.",
    )

    # Auditing timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def project_context(self):
        return self.task.project

    class Meta:
        ordering = ["-logged_at", "-created_at"]

    def clean(self):
        super().clean()

        # 1. Check if the log is currently locked
        if not self._state.adding:
            original = TimeLog.objects.get(pk=self.pk)
            if original.is_locked:
                raise ValidationError("This time log is locked and cannot be modified.")

        # 2. Enforce positive duration check
        if self.duration <= Decimal("0.00"):
            raise ValidationError({"duration": "Logged duration must be positive."})

        # 3. Ensure logging user is an active member of the project
        active_members = self.task.project.active_member_ids
        if self.user_id and self.user_id not in active_members:
            raise ValidationError(
                {"user": "The logging user must be an active member of this project."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.task.update_time_spent()

    def delete(self, *args, **kwargs):
        if self.is_locked:
            raise ValidationError("This time log is locked and cannot be deleted.")
        task = self.task
        super().delete(*args, **kwargs)
        task.update_time_spent()

    def __str__(self):
        return f"{self.user.username} - {self.task.project.code}-{self.task.number} ({self.duration}h)"
