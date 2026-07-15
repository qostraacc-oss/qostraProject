from django.urls import path
from sprints.views import (
    SprintListCreateAPIView,
    SprintDetailAPIView,
)

urlpatterns = [
    path(
        "<uuid:workspace_id>/projects/<uuid:project_id>/sprints/",
        SprintListCreateAPIView.as_view(),
        name="sprint-list-create",
    ),
    path(
        "<uuid:workspace_id>/sprints/<uuid:sprint_id>/",
        SprintDetailAPIView.as_view(),
        name="sprint-detail",
    ),
]
