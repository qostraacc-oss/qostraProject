from django.urls import path
from timelogs.views import TimeLogListCreateAPIView, TimeLogDetailAPIView

urlpatterns = [
    path(
        "<uuid:workspace_id>/tasks/<uuid:task_id>/timelogs/",
        TimeLogListCreateAPIView.as_view(),
        name="timelog-list-create",
    ),
    path(
        "<uuid:workspace_id>/timelogs/<uuid:pk>/",
        TimeLogDetailAPIView.as_view(),
        name="timelog-detail",
    ),
]
