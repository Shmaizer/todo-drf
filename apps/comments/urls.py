from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentDetailAPIView

urlpatterns = [
    path(
        "tasks/<int:pk>/comments/",
        CommentDetailAPIView.as_view(),
        name="comment-detail",
    ),
]
