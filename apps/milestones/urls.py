from django.urls import path
from milestones.views import (
    MilestoneListCreateAPIView,
    MilestoneDetailAPIView,
    MilestoneReorderAPIView,
)

urlpatterns = [
    path(
        "<uuid:workspace_id>/projects/<uuid:project_id>/milestones/",
        MilestoneListCreateAPIView.as_view(),
        name="milestone-list-create",
    ),
    path(
        "<uuid:workspace_id>/projects/<uuid:project_id>/milestones/reorder/",
        MilestoneReorderAPIView.as_view(),
        name="milestone-reorder",
    ),
    path(
        "<uuid:workspace_id>/milestones/<uuid:milestone_id>/",
        MilestoneDetailAPIView.as_view(),
        name="milestone-detail",
    ),
]
