from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserAuthLoginView, UserCreateView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, "users")

urlpatterns = [
    path("auth/register", UserCreateView.as_view(), name="auth-register"),
    path("auth/login", UserAuthLoginView.as_view(), name="auth-login"),
] + router.urls
