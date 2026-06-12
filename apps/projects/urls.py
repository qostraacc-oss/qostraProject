from django.urls import path
from apps.projects.views import (
    ProjectListCreateAPIView,
    ProjectDetailAPIView,
    ProjectMemberListAPIView,
    ProjectMemberDetailAPIView,
)

urlpatterns = [
    # Projects
    path('', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('<uuid:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    
    # Project Members
    path('<uuid:project_id>/members/', ProjectMemberListAPIView.as_view(), name='project-member-list-create'),
    path('<uuid:project_id>/members/<uuid:pk>/', ProjectMemberDetailAPIView.as_view(), name='project-member-detail'),
]
