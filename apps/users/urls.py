from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivateView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserAuthLoginView,
    UserCreateView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, "users")

urlpatterns = [
    path("auth/register", UserCreateView.as_view(), name="auth-register"),
    path("auth/login", UserAuthLoginView.as_view(), name="auth-login"),
    path("activate/", ActivateView.as_view(), name="user-activate"),
    path(
        "password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
] + router.urls
