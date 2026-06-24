from django.urls import path, include
from projects.views import (
    ProjectListCreateAPIView,
    ProjectDetailAPIView,
    ProjectMemberListAPIView,
    ProjectMemberDetailAPIView,
    ProjectInvitationListCreateAPIView,
    ResendInvitationAPIView,
    RevokeInvitationAPIView,
    AcceptInvitationAPIView,
    DeclineInvitationAPIView,
    UserPendingInvitationsAPIView,
    InvitationDetailAPIView,
)

urlpatterns = [
    # Global/User pending invitations (no workspace_id prefix)
    path(
        "invitations/",
        UserPendingInvitationsAPIView.as_view(),
        name="user-invitations-list",
    ),
    path(
        "invitations/<uuid:invitation_id>/",
        InvitationDetailAPIView.as_view(),
        name="user-invitation-detail",
    ),
    # Workspace-specific project URLs
    # Projects
    path(
        "<uuid:workspace_id>/",
        ProjectListCreateAPIView.as_view(),
        name="project-list-create",
    ),
    path(
        "<uuid:workspace_id>/<uuid:pk>/",
        ProjectDetailAPIView.as_view(),
        name="project-detail",
    ),
    # Project Members
    path(
        "<uuid:workspace_id>/<uuid:project_id>/members/",
        ProjectMemberListAPIView.as_view(),
        name="project-member-list-create",
    ),
    path(
        "<uuid:workspace_id>/<uuid:project_id>/members/<uuid:pk>/",
        ProjectMemberDetailAPIView.as_view(),
        name="project-member-detail",
    ),
    # Project Invitations
    path(
        "<uuid:workspace_id>/<uuid:project_id>/invitations/",
        ProjectInvitationListCreateAPIView.as_view(),
        name="project-invitation-list-create",
    ),
    path(
        "<uuid:workspace_id>/invitations/<uuid:invitation_id>/resend/",
        ResendInvitationAPIView.as_view(),
        name="project-invitation-resend",
    ),
    path(
        "<uuid:workspace_id>/invitations/<uuid:invitation_id>/revoke/",
        RevokeInvitationAPIView.as_view(),
        name="project-invitation-revoke",
    ),
    path(
        "<uuid:workspace_id>/invitations/<uuid:invitation_id>/accept/",
        AcceptInvitationAPIView.as_view(),
        name="project-invitation-accept",
    ),
    path(
        "<uuid:workspace_id>/invitations/<uuid:invitation_id>/decline/",
        DeclineInvitationAPIView.as_view(),
        name="project-invitation-decline",
    ),
    # Tasks URLs
    path("", include("apps.tasks.urls")),
]
