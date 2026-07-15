from django.urls import path
from tasks.views import (
    BoardListCreateAPIView,
    BoardDetailAPIView,
    ColumnListCreateAPIView,
    ColumnDetailAPIView,
    ColumnReorderAPIView,
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskMoveAPIView,
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
    # Task Routes
    path(
        "<uuid:workspace_id>/projects/<uuid:project_id>/tasks/",
        TaskListCreateAPIView.as_view(),
        name="task-list-create",
    ),
    path(
        "<uuid:workspace_id>/tasks/<uuid:task_id>/",
        TaskDetailAPIView.as_view(),
        name="task-detail",
    ),
    path(
        "<uuid:workspace_id>/tasks/<uuid:task_id>/move/",
        TaskMoveAPIView.as_view(),
        name="task-move",
    ),
]


