from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from rest_framework import exceptions, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_core import jwt_utils
from apps.core.models import TokenBlacklist, User
from apps.rbac.permissions import RBACPermission
from apps.users.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UpdateMeSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """Регистрация нового пользователя.

    Не требует аутентификации. Создаёт пользователя с захешированным паролем.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def post(self, request: Request) -> Response:
        """Создать нового пользователя и вернуть его данные."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.all_objects.create(
            full_name=data["full_name"],
            email=data["email"],
        )
        user.set_password(data["password"])
        user.save(update_fields=["password_hash"])

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Аутентификация пользователя по email и паролю.

    При успехе возвращает JWT access-токен.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def post(self, request: Request) -> Response:
        """Проверить учётные данные и выдать JWT-токен."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.all_objects.get(email=data["email"])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid credentials.")

        if not user.is_active:
            return Response(
                {"detail": "Пользователь неактивен."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(data["password"]):
            raise exceptions.AuthenticationFailed("Invalid credentials.")

        token, jti, exp = jwt_utils.create_access_token(user.id)

        response_data: Dict[str, Any] = {
            "access": token,
            "user": UserSerializer(user).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class MeView(APIView):
    """Профиль текущего аутентифицированного пользователя.

    GET  — получить данные.
    PATCH — обновить имя или email.
    """

    permission_classes = [RBACPermission]

    def get(self, request: Request) -> Response:
        """Вернуть данные текущего пользователя."""
        user = request.user
        assert isinstance(user, User)
        return Response(UserSerializer(user).data)

    def patch(self, request: Request) -> Response:
        """Обновить имя или email текущего пользователя."""
        user = request.user
        assert isinstance(user, User)
        serializer = UpdateMeSerializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        update_fields: list[str] = []
        if "full_name" in data:
            user.full_name = data["full_name"]
            update_fields.append("full_name")
        if "email" in data:
            user.email = data["email"]
            update_fields.append("email")

        if update_fields:
            update_fields.append("updated_at")
            user.save(update_fields=update_fields)

        return Response(UserSerializer(user).data)


class DeleteMeView(APIView):
    """Мягкое удаление текущего пользователя.

    Устанавливает is_active=False и инвалидирует текущий токен.
    """

    permission_classes = [RBACPermission]

    def post(self, request: Request) -> Response:
        """Деактивировать аккаунт и заблокировать токен."""
        user = request.user
        assert isinstance(user, User)
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        _blacklist_current_token(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    """Выход из системы с инвалидацией текущего JWT."""

    permission_classes = [RBACPermission]

    def post(self, request: Request) -> Response:
        """Добавить токен в чёрный список и завершить сессию."""
        _blacklist_current_token(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


def _blacklist_current_token(request: Request) -> None:
    """Извлечь JWT из заголовка запроса и поместить его в чёрный список.

    Если токен отсутствует или повреждён — ничего не делает.
    """
    auth_header = request.headers.get("Authorization") or ""
    parts = auth_header.split()
    if len(parts) != 2:
        return
    token = parts[1]
    try:
        payload = jwt_utils.decode_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            if isinstance(exp, dt.datetime):
                expires_at = exp if exp.tzinfo else exp.replace(tzinfo=dt.timezone.utc)
            else:
                expires_at = dt.datetime.fromtimestamp(exp, tz=dt.timezone.utc)
            TokenBlacklist.objects.get_or_create(
                token_jti=jti,
                defaults={"expires_at": expires_at},
            )
    except Exception:
        pass
