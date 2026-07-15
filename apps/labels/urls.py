from django.urls import path
from labels.views import (
    LabelListCreateAPIView,
    LabelDetailAPIView,
    AllLabelsListAPIView,
)


urlpatterns = [
    path(
        "<uuid:workspace_id>/labels/",
        LabelListCreateAPIView.as_view(),
        name="workspace-label-list-create",
    ),
    path(
        "<uuid:workspace_id>/labels/all/",
        AllLabelsListAPIView.as_view(),
        name="all-labels-list",
    ),
    path(
        "<uuid:workspace_id>/projects/<uuid:project_id>/labels/",
        LabelListCreateAPIView.as_view(),
        name="project-label-list-create",
    ),
    path(
        "<uuid:workspace_id>/labels/<uuid:label_id>/",
        LabelDetailAPIView.as_view(),
        name="label-detail",
    ),
]
