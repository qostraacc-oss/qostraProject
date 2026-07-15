import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from common.permissions import WorkspaceResourceMixin
from projects.models import Project


class Label(WorkspaceResourceMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # External multi-tenant reference
    workspace_id = models.UUIDField(db_index=True)

    # Optional project scoping (Null = Workspace wide, Not Null = Project specific)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="project_scoped_labels",
    )

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, blank=True)

    # Hex Color Code
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(r"^#[0-9A-Fa-f]{6}$", _("Enter a valid 6-digit hex color"))
        ],
        default="#64748B",
    )

    description = models.TextField(blank=True)

    # Fractional position ordering
    position = models.DecimalField(max_digits=30, decimal_places=20, default=0.0)

    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def project_context(self):
        return self.project

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (("workspace_id", "project", "name"),)
        ordering = ["position", "created_at"]

    def __str__(self):
        return f"{self.name} ({self.workspace_id})"
