from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from .models import User
from .serializers import UserSerializer
from .utils import create_jwt_token

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateView(APIView):
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

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(data.get("password")),
        )
        token = create_jwt_token(user)
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

        token = create_jwt_token(user)
        return JsonResponse(
            {
                "user_id": user.id,
                "token": token.get("access"),
                "refresh-token": token.get("refresh"),
            },
            status=200,
        )
