from django.urls import path
from apps.accounts.views import ProfileAPIView

urlpatterns = [
    path("profile/", ProfileAPIView.as_view(), name="profile"),
]
