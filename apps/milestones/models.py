import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from common.permissions import WorkspaceResourceMixin
from projects.models import Project


class Milestone(WorkspaceResourceMixin, models.Model):
    class StatusChoices(models.TextChoices):
        PLANNED = "planned", _("Planned")
        ACTIVE = "active", _("Active")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="milestones",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=20, blank=True, default="")

    archived_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_milestones",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def project_context(self):
        return self.project

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def task_count(self):
        return self.tasks.count()

    @property
    def completed_task_count(self):
        return self.tasks.filter(column__category="DONE").count()

    @property
    def progress(self):
        total = self.task_count
        if total == 0:
            return 0.0
        return round((self.completed_task_count / total) * 100.0, 2)

    @property
    def overdue_task_count(self):
        today = timezone.now().date()
        return self.tasks.filter(due_date__lt=today, column__category="OPEN").count()

    class Meta:
        ordering = ["position", "due_date"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError({"due_date": _("Due date must be after start date.")})

        # Ensure active milestone name is unique within the project
        if self.name and self.project:
            query = Milestone.objects.filter(
                project=self.project, name=self.name, archived_at__isnull=True
            )
            if self.pk:
                query = query.exclude(pk=self.pk)
            if query.exists():
                raise ValidationError(
                    {
                        "name": _(
                            "A milestone with this name already exists in this project."
                        )
                    }
                )

        # Ensure created_by is a project member
        if (
            self.created_by_id
            and self.created_by_id not in self.project.active_member_ids
        ):
            raise ValidationError(
                {
                    "created_by": _(
                        "The creator must be an active member of this project."
                    )
                }
            )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            self.full_clean()

            # Auto-assign position if not specified/defaulted
            if self.position is None:
                max_pos = Milestone.objects.filter(project=self.project).aggregate(
                    max_pos=models.Max("position")
                )["max_pos"]
                self.position = 0 if max_pos is None else max_pos + 1

        # Check status transitions for completed_at setting
        if self.status == self.StatusChoices.COMPLETED:
            if not self.completed_at:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None

        super().save(*args, **kwargs)
