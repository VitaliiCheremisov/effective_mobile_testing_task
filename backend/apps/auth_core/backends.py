from __future__ import annotations

from typing import Optional, Tuple

import jwt
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from apps.auth_core import jwt_utils
from apps.core.models import TokenBlacklist, User
from django.utils import timezone


class JWTAuthentication(BaseAuthentication):
    """Аутентификация на основе JWT (AuthN-слой).

    Извлекает токен из заголовка Authorization: Bearer <token>,
    проверяет подпись, срок действия и наличие в чёрном списке.
    """

    keyword = "Bearer"

    def authenticate(self, request: Request) -> Optional[Tuple[User, None]]:  # type: ignore[override]
        """Аутентифицировать запрос по JWT-токену.

        Возвращает кортеж (user, None) при успехе или None, если заголовок отсутствует.
        Выбрасывает AuthenticationFailed при невалидном или отозванном токене.
        """
        auth_header = request.headers.get("Authorization") or ""
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed(
                "Неверный формат заголовка Authorization."
            )

        token = parts[1]

        try:
            payload = jwt_utils.decode_token(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Срок действия токена истёк.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Невалидный токен.")

        jti = payload.get("jti")
        user_id = payload.get("user_id")
        if not jti or not user_id:
            raise exceptions.AuthenticationFailed("Некорректный payload токена.")

        now = timezone.now()
        if TokenBlacklist.objects.filter(token_jti=jti, expires_at__gt=now).exists():
            raise exceptions.AuthenticationFailed("Токен отозван.")

        try:
            user = User.all_objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Пользователь не найден.")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("Пользователь неактивен.")

        return user, None

    def authenticate_header(self, request: Request) -> str:
        """Вернуть значение WWW-Authenticate для ответов 401."""
        return self.keyword
