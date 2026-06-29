import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project


class Board(models.Model):
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

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"], name="unique_project_board_name"
            )
        ]

    def __str__(self):
        return self.name


class Column(models.Model):
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


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", _("Low")
        MEDIUM = "MEDIUM", _("Medium")
        HIGH = "HIGH", _("High")
        CRITICAL = "CRITICAL", _("Critical")

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")

    column = models.ForeignKey(Column, on_delete=models.PROTECT, related_name="tasks")

    number = models.PositiveIntegerField(db_index=True, editable=False)

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subtasks",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True, null=True)

    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_tasks",
    )

    start_date = models.DateField(null=True, blank=True)

    due_date = models.DateField(null=True, blank=True)

    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "number"], name="unique_project_task_number"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.number:
            max_num = Task.objects.filter(project=self.project).aggregate(
                max_val=models.Max("number")
            )["max_val"]
            self.number = (max_num or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
