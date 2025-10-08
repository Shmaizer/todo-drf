from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TaskAssignAPIView,
    TaskDetailAPIView,
    TaskListCreateAPIView,
    TaskPriorityAPIView,
    TaskStatusAPIView,
)

# router = DefaultRouter()
# router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("tasks/", TaskListCreateAPIView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/assign/", TaskAssignAPIView.as_view(), name="task-assign"),
    path(
        "tasks/<int:pk>/update-status/",
        TaskStatusAPIView.as_view(),
        name="task-update-status",
    ),
    path(
        "tasks/<int:pk>/priority/",
        TaskPriorityAPIView.as_view(),
        name="task-update-priority",
    ),
]
