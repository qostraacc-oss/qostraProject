import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class Project(models.Model):
    class StatusChoices(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    class PriorityChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # External References
    workspace_id = models.UUIDField(db_index=True)

    client_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects",
    )

    # Core Information
    name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        blank=True,
    )

    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z][A-Z0-9_]{1,19}$",
                message=(
                    "Project code must start with an uppercase "
                    "letter and contain only uppercase letters, "
                    "numbers, and underscores."
                ),
            )
        ],
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    # State
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PLANNED,
        db_index=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
        db_index=True,
    )

    # Timeline
    start_date = models.DateField(
        null=True,
        blank=True,
    )

    target_end_date = models.DateField(
        null=True,
        blank=True,
    )

    actual_end_date = models.DateField(
        null=True,
        blank=True,
    )

    # Lifecycle
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["workspace_id", "code"],
                name="unique_workspace_project_code",
            ),
            models.UniqueConstraint(
                fields=["workspace_id", "slug"],
                name="unique_workspace_project_slug",
            ),
        ]

        indexes = [
            models.Index(
                fields=["workspace_id", "status"],
                name="project_ws_status_idx",
            ),
            models.Index(
                fields=["workspace_id", "priority"],
                name="project_ws_priority_idx",
            ),
        ]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while (
                Project.objects.filter(
                    workspace_id=self.workspace_id,
                    slug=slug,
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

        if is_new:
            ProjectMember.objects.get_or_create(
                project=self,
                user=self.created_by,
                defaults={
                    "role": ProjectMember.RoleChoices.OWNER,
                    "workspace_id": self.workspace_id,
                    "created_by": self.created_by,
                }
            )

    @property
    def is_archived(self):
        return self.archived_at is not None

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectMember(models.Model):
    class RoleChoices(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    workspace_id = models.UUIDField(db_index=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBER,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_project_members",
    )

    removed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project Member"
        verbose_name_plural = "Project Members"

        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                condition=Q(removed_at__isnull=True),
                name="unique_active_project_member",
            )
        ]

        indexes = [
            models.Index(
                fields=["workspace_id"],
                name="project_member_ws_idx",
            ),
            models.Index(
                fields=["project", "role"],
                name="project_member_role_idx",
            ),
        ]

    @property
    def is_removed(self):
        return self.removed_at is not None

    def __str__(self):
        return f"{self.user} ({self.role})"
