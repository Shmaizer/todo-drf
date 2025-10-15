import os

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from .models import EmailCode, User
from .serializers import (
    ActivateSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)
from .tasks import send_email_code
from .utils import (
    create_jwt_token,
    expiry_time_for_purpose,
    generate_numeric_code,
    hash_code,
    verify_code_hash,
)

# Create your views here.

MAX_CODE_ATTEMPTS = int(os.getenv("MAX_CODE_ATTEMPTS"))


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        required_fields = ["username", "email", "password"]
        if not all(data.get(field) for field in required_fields):
            return JsonResponse({"error": "All fields be required!"}, status=400)
        username = data.get("username")
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists!"}, status=400)
        email = data.get("email")
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists!"}, status=400)

        # user = User.objects.create(
        #     username=username,
        #     email=email,
        #     password=make_password(data.get("password")),
        # )

        ser = UserSerializer(data=data)
        ser.is_valid(raise_exception=True)
        user = ser.save()

        code = generate_numeric_code()
        code_hash = hash_code(code)
        expires_at = expiry_time_for_purpose("activation")
        token = create_jwt_token(user)

        EmailCode.objects.create(
            user=user, purpose="activation", code_hash=code_hash, expires_at=expires_at
        )

        # Rate limiting отправки (Redis, cache)
        key = f"rl:send:{user.email}"
        sent = cache.get(key, 0)
        if sent >= MAX_CODE_ATTEMPTS:  # или другое значение лимита
            return JsonResponse({"error": "Too many requests"}, status=429)
        cache.set(key, sent + 1, 60)  # окно 60 секунд

        # Отправляем email асинхронно
        send_email_code.delay(user.email, code, "activation")

        return JsonResponse(
            {
                "message": "User created successfully",
                "user_id": user.id,
                "token": token.get("access"),
                "refresh-token": token.get("refresh"),
            },
            status=201,
        )


class UserAuthLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        required_fields = ["username", "password"]
        if not all(data.get(field) for field in required_fields):
            return JsonResponse({"error": "All fields are required."}, status=400)
        try:
            user = User.objects.get(username=data.get("username"))
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid username or password."}, status=400)
        if not check_password(data.get("password"), user.password):
            return JsonResponse({"error": "Invalid username or password."}, status=400)
        if not user.is_active:
            return JsonResponse({"error": "User account is disabled."}, status=400)

        token = create_jwt_token(user)
        return JsonResponse(
            {
                "user_id": user.id,
                "token": token.get("access"),
                "refresh-token": token.get("refresh"),
            },
            status=200,
        )


# Активация аккаунта по коду
class ActivateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)

        codes = EmailCode.objects.filter(
            user=user, purpose="activation", used=False
        ).order_by("-created_at")
        if not codes.exists():
            return JsonResponse({"error": "Activation code not found."}, status=400)

        code_obj = codes.first()

        # Проверяем: не истёк ли код
        if code_obj.is_expired():
            return JsonResponse({"error": "Code expired."}, status=400)

        # Проверка попыток
        if code_obj.attempts >= MAX_CODE_ATTEMPTS:
            return JsonResponse({"error": "Too many attempts."}, status=429)

        # Проверка кода
        if verify_code_hash(code, code_obj.code_hash):
            with transaction.atomic():
                user.is_active = True
                user.save(update_fields=["is_active"])
                code_obj.used = True
                code_obj.save(update_fields=["used"])
            token = create_jwt_token(user)
            return JsonResponse(
                {"message": "Account activated", "token": token.get("access")},
                status=200,
            )
        else:
            code_obj.attempts += 1
            code_obj.save(update_fields=["attempts"])
            remaining = MAX_CODE_ATTEMPTS - code_obj.attempts
            return JsonResponse(
                {"error": "Invalid code", "remaining_attempts": remaining}, status=400
            )


# Запрос кода для сброса пароля
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Не раскрываем, существует ли email или нет
            return JsonResponse(
                {"message": "If the email exists, a reset code was sent"}, status=200
            )

        key = f"rl:send_reset:{email}"
        sent = cache.get(key, 0)
        if sent >= MAX_CODE_ATTEMPTS:
            return JsonResponse({"error": "Too many requests"}, status=429)
        cache.set(key, sent + 1, 60)

        code = generate_numeric_code()
        code_hash = hash_code(code)
        expires_at = expiry_time_for_purpose("password_reset")

        EmailCode.objects.create(
            user=user,
            purpose="password_reset",
            code_hash=code_hash,
            expires_at=expires_at,
        )

        send_email_code.delay(user.email, code, "password_reset")
        return JsonResponse(
            {"message": "If the email exists, a reset code was sent"}, status=200
        )


# Подтверждение кода сброса и установка нового пароля
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid email or code."}, status=400)

        codes = EmailCode.objects.filter(
            user=user, purpose="password_reset", used=False
        ).order_by("-created_at")
        if not codes.exists():
            return JsonResponse({"error": "Reset code not found."}, status=400)

        code_obj = codes.first()

        if code_obj.is_expired():
            return JsonResponse({"error": "Code expired."}, status=400)
        if code_obj.attempts >= MAX_CODE_ATTEMPTS:
            return JsonResponse({"error": "Too many attempts."}, status=429)

        if verify_code_hash(code, code_obj.code_hash):
            with transaction.atomic():
                user.set_password(new_password)
                user.save()
                code_obj.used = True
                code_obj.save(update_fields=["used"])
            return JsonResponse({"message": "Password has been reset."}, status=200)
        else:
            code_obj.attempts += 1
            code_obj.save(update_fields=["attempts"])
            remaining = MAX_CODE_ATTEMPTS - code_obj.attempts
            return JsonResponse(
                {"error": "Invalid code", "remaining_attempts": remaining}, status=400
            )
