import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from common.permissions import WorkspaceResourceMixin


class Board(WorkspaceResourceMixin, models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="boards"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def project_context(self):
        return self.project

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"], name="unique_project_board_name"
            )
        ]

    def __str__(self):
        return self.name


class Column(WorkspaceResourceMixin, models.Model):
    @property
    def project_context(self):
        return self.board.project

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Category(models.TextChoices):
        OPEN = "OPEN", _("Open")
        DONE = "DONE", _("Done")
        CANCELLED = "CANCELLED", _("Cancelled")

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")

    name = models.CharField(max_length=100)

    position = models.PositiveIntegerField(default=0)

    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OPEN
    )

    color = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name


class Task(WorkspaceResourceMixin, models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    @property
    def project_context(self):
        return self.project

    # -------------------------
    # Choices
    # -------------------------

    class Type(models.TextChoices):
        TASK = "TASK", _("Task")
        BUG = "BUG", _("Bug")
        STORY = "STORY", _("Story")
        EPIC = "EPIC", _("Epic")
        FEATURE = "FEATURE", _("Feature")
        IMPROVEMENT = "IMPROVEMENT", _("Improvement")
        SPIKE = "SPIKE", _("Spike")

    class Priority(models.TextChoices):
        LOW = "LOW", _("Low")
        MEDIUM = "MEDIUM", _("Medium")
        HIGH = "HIGH", _("High")
        CRITICAL = "CRITICAL", _("Critical")

    class Status(models.TextChoices):
        TODO = "TODO", _("To Do")
        IN_PROGRESS = "IN_PROGRESS", _("In Progress")
        IN_REVIEW = "IN_REVIEW", _("In Review")
        TESTING = "TESTING", _("Testing")
        DONE = "DONE", _("Done")
        BLOCKED = "BLOCKED", _("Blocked")
        CANCELLED = "CANCELLED", _("Cancelled")

    # -------------------------
    # Identity
    # -------------------------

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    number = models.PositiveIntegerField(
        editable=False,
        db_index=True,
    )

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.TASK,
    )

    # -------------------------
    # Workflow
    # -------------------------

    column = models.ForeignKey(
        Column,
        on_delete=models.PROTECT,
        related_name="tasks",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )

    position = models.PositiveIntegerField(default=0)

    # -------------------------
    # Content
    # -------------------------

    title = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        default="",
    )

    # -------------------------
    # Planning
    # -------------------------

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    estimate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated hours",
    )

    time_spent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Logged hours",
    )

    milestone = models.ForeignKey(
        "milestones.Milestone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    labels = models.ManyToManyField(
        "labels.Label",
        blank=True,
        related_name="tasks",
    )



    # -------------------------
    # People
    # -------------------------

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_tasks",
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    watchers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="watching_tasks",
    )

    # -------------------------
    # Dates
    # -------------------------

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # -------------------------
    # Metadata
    # -------------------------

    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "column",
            "position",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["project", "number"],
                name="unique_project_task_number",
            )
        ]

    def __str__(self):
        return f"{self.project.code}-{self.number} {self.title}"

    def clean(self):
        super().clean()

        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError({"due_date": "Due date must be after start date."})

        if self.column and self.column.board.project != self.project:
            raise ValidationError(
                _("The selected column does not belong to a board in this project.")
            )

        if self.milestone:
            if self.milestone.project != self.project:
                raise ValidationError(
                    {
                        "milestone": _(
                            "The selected milestone does not belong to this project."
                        )
                    }
                )
            if self.milestone.project.workspace_id != self.project.workspace_id:
                raise ValidationError(
                    {
                        "milestone": _(
                            "The selected milestone is in a different workspace."
                        )
                    }
                )

        active_member_ids = self.project.active_member_ids

        # Enforce that the assignee is an active project member
        if self.assignee_id and self.assignee_id not in active_member_ids:
            raise ValidationError(
                {
                    "assignee": _(
                        "The assignee must be an active member of this project."
                    )
                }
            )

        # Enforce that the reporter is an active project member
        if self.reporter_id and self.reporter_id not in active_member_ids:
            raise ValidationError(
                {
                    "reporter": _(
                        "The reporter must be an active member of this project."
                    )
                }
            )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            self.full_clean()

        if not self.number:
            from django.db import transaction

            with transaction.atomic():
                max_num = (
                    Task.objects.select_for_update()
                    .filter(project=self.project)
                    .aggregate(max_val=models.Max("number"))["max_val"]
                )
                self.number = (max_num or 0) + 1
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
