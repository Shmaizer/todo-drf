import os
from pathlib import Path

import environ
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import User

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != env.str("JWT_PREFIX"):
                raise AuthenticationFailed("Invalid token prefix")
        except ValueError:
            raise AuthenticationFailed("Invalid token prefix")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        username = payload.get("username")
        if not username:
            raise AuthenticationFailed("Username not found")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, None)
