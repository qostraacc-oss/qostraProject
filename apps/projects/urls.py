from django.urls import path
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
)

urlpatterns = [
    # Projects
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("<uuid:pk>/", ProjectDetailAPIView.as_view(), name="project-detail"),
    # Project Members
    path(
        "<uuid:project_id>/members/",
        ProjectMemberListAPIView.as_view(),
        name="project-member-list-create",
    ),
    path(
        "<uuid:project_id>/members/<uuid:pk>/",
        ProjectMemberDetailAPIView.as_view(),
        name="project-member-detail",
    ),
    # Project Invitations
    path(
        "<uuid:project_id>/invitations/",
        ProjectInvitationListCreateAPIView.as_view(),
        name="project-invitation-list-create",
    ),
    path(
        "invitations/<uuid:invitation_id>/resend/",
        ResendInvitationAPIView.as_view(),
        name="project-invitation-resend",
    ),
    path(
        "invitations/<uuid:invitation_id>/revoke/",
        RevokeInvitationAPIView.as_view(),
        name="project-invitation-revoke",
    ),
    path(
        "invitations/<uuid:invitation_id>/accept/",
        AcceptInvitationAPIView.as_view(),
        name="project-invitation-accept",
    ),
    path(
        "invitations/<uuid:invitation_id>/decline/",
        DeclineInvitationAPIView.as_view(),
        name="project-invitation-decline",
    ),
]
