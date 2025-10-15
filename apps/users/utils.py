import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import environ
import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password

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


def generate_numeric_code(length: int = 6) -> str:
    # Случайное число от 0 до 10^length – 1, с ведущими нулями
    n = secrets.randbelow(10**length)
    return str(n).zfill(length)


def hash_code(code: str) -> str:
    # Использует встроенный Django-хешер (PBKDF2 / соль и т.д.)
    return make_password(code)


def verify_code_hash(raw_code: str, stored_hash: str) -> bool:
    # Проверяет raw_code и хеш — вернёт True, если совпадают
    return check_password(raw_code, stored_hash)


def expiry_time_for_purpose(purpose: str):
    # Возвращает datetime, до которого код будет действителен
    if purpose == "activation":
        minutes = os.getenv("ACTIVATION_CODE_EXPIRE_MINUTES")
    else:
        minutes = os.getenv("RESET_CODE_EXPIRE_MINUTES")
    return datetime.now(timezone.utc) + timedelta(minutes=int(minutes))
