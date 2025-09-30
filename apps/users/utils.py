import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import environ
import jwt
from django.utils import timezone as django_timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


def create_jwt_token(user):
    access_payload = {
        "username": user.username,
        "type": "acccess",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=int(os.getenv("ACCESS_TOKEN_LIFETIME"))),
        "iat": datetime.now(timezone.utc),
    }
    access_token = jwt.encode(
        access_payload, os.getenv("SECRET_KEY"), algorithm="HS256"
    )

    refresh_payload = {
        "username": user.username,
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME"))),
        "iat": datetime.now(timezone.utc),
    }
    refresh_token = jwt.encode(
        refresh_payload, os.getenv("SECRET_KEY"), algorithm="HS256"
    )

    return {
        "access": access_token,
        "refresh": refresh_token,
    }
