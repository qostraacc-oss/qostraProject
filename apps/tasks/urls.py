from django.urls import path
from tasks.views import BoardListCreateAPIView, BoardDetailAPIView

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
]
