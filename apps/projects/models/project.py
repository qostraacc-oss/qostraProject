import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


from common.permissions import WorkspaceResourceMixin


class ProjectQuerySet(models.QuerySet):
    def for_workspace(self, workspace_id, user):
        """
        Returns projects associated with the workspace:
        1. Owned/created by user in this workspace.
        2. Or mapped by user to this workspace as an active project member.
        """
        return self.filter(
            models.Q(workspace_id=workspace_id, created_by=user)
            | models.Q(
                members__user=user,
                members__workspace_id=workspace_id,
                members__removed_at__isnull=True,
            )
        ).distinct()


class Project(WorkspaceResourceMixin, models.Model):
    objects = ProjectQuerySet.as_manager()

    @property
    def project_context(self):
        return self

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

    labels = models.ManyToManyField(

        "labels.Label",
        blank=True,
        related_name="projects",
    )

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
                },
            )

    @property
    def active_member_ids(self):
        if not hasattr(self, "_active_member_ids_cache"):
            self._active_member_ids_cache = set(
                self.members.filter(removed_at__isnull=True).values_list(
                    "user_id", flat=True
                )
            )
        return self._active_member_ids_cache

    @property
    def is_archived(self):
        return self.archived_at is not None

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectMember(WorkspaceResourceMixin, models.Model):
    class RoleChoices(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    @property
    def project_context(self):
        return self.project

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
