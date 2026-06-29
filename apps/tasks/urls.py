from django.urls import path
from tasks.views import (
    BoardListCreateAPIView,
    BoardDetailAPIView,
    ColumnListCreateAPIView,
    ColumnDetailAPIView,
    ColumnReorderAPIView,
)

urlpatterns = [
    path(
        "<uuid:workspace_id>/<uuid:project_id>/boards/",
        BoardListCreateAPIView.as_view(),
        name="board-list-create",
    ),
    path(
        "<uuid:workspace_id>/boards/<uuid:board_id>/",
        BoardDetailAPIView.as_view(),
        name="board-detail",
    ),
    path(
        "<uuid:workspace_id>/boards/<uuid:board_id>/columns/",
        ColumnListCreateAPIView.as_view(),
        name="column-list-create",
    ),
    path(
        "<uuid:workspace_id>/boards/<uuid:board_id>/columns/reorder/",
        ColumnReorderAPIView.as_view(),
        name="column-reorder",
    ),
    path(
        "<uuid:workspace_id>/columns/<uuid:column_id>/",
        ColumnDetailAPIView.as_view(),
        name="column-detail",
    ),
]
