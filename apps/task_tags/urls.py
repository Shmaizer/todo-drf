from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskTagsDeleteAPIView, TaskTagsDetailAPIView

# router = DefaultRouter()
# router.register(r"task_tags", TaskTagsViewSet)

urlpatterns = [
    path(
        "tasks/<int:pk>/tags/", TaskTagsDetailAPIView.as_view(), name="task-tags-detail"
    ),
    path(
        "tasks/<int:pk>/tags/<int:tag_id>/",
        TaskTagsDeleteAPIView.as_view(),
        name="task-tags-delete",
    ),
]
