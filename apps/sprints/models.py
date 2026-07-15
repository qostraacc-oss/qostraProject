import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from common.permissions import WorkspaceResourceMixin
from projects.models import Project


class Sprint(WorkspaceResourceMixin, models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", _("Planned")
        ACTIVE = "ACTIVE", _("Active")
        COMPLETED = "COMPLETED", _("Completed")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="sprints",
    )

    name = models.CharField(max_length=255)
    goal = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def project_context(self):
        return self.project

    class Meta:
        ordering = ["start_date", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"], name="unique_project_sprint_name"
            )
        ]

    def __str__(self):
        return self.name
