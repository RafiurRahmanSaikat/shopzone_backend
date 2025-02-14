from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
from core.pagination import CustomPageNumberPagination
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import IsAdmin, IsOwner
from .serializers import (
    PasswordChangeSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action == "destroy":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=["get", "put", "patch"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        print("Authenticated user:", request.user)
        if request.method in ["PUT", "PATCH", "POST"]:
            serializer = UserUpdateSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            request.user.clear_cache()
            return Response(serializer.data)

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        request.user.clear_cache()
        return Response({"detail": "Password changed successfully."})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Optional: Delete all tokens for this user
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                token.blacklist()

            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Invalid refresh token or logout failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
