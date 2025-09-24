from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskTagsViewSet

router = DefaultRouter()
router.register(r"task_tags", TaskTagsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
