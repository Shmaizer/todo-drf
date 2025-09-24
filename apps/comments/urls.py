from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
