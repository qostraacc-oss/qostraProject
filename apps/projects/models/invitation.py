import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from .project import Project, ProjectMember


def default_expires_at():
    return timezone.now() + timedelta(days=7)


class ProjectInvitation(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace_id = models.UUIDField(db_index=True)

    # Direct relation to Project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="invitations",
    )

    # Invitee Identity (UUID-based)
    invitee_id = models.UUIDField(db_index=True)
    invitee_email = models.EmailField(db_index=True)

    role = models.CharField(
        max_length=20,
        choices=ProjectMember.RoleChoices.choices,
        default=ProjectMember.RoleChoices.MEMBER,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Audit Information
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_project_invitations",
    )

    # Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expires_at)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project Invitation"
        verbose_name_plural = "Project Invitations"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "invitee_email"],
                condition=models.Q(status="pending"),
                name="unique_pending_invitation_per_project",
            )
        ]

    def is_expired(self):
        return (
            self.status == self.StatusChoices.PENDING
            and timezone.now() > self.expires_at
        )

    def __str__(self):
        return f"Invite for {self.invitee_email} to {self.project.code} ({self.status})"
