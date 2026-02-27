from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.core.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    """Сериализатор для отображения данных пользователя."""

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class RegisterSerializer(serializers.Serializer[dict[str, Any]]):
    """Валидация данных при регистрации нового пользователя."""

    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверить совпадение паролей и уникальность email."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        if User.all_objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return attrs


class LoginSerializer(serializers.Serializer[dict[str, Any]]):
    """Валидация учётных данных при входе в систему."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UpdateMeSerializer(serializers.Serializer[dict[str, Any]]):
    """Валидация данных при обновлении профиля пользователя."""

    full_name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)

    def validate_email(self, value: str) -> str:
        """Проверить, что новый email не занят другим пользователем."""
        current_user: User = self.context["user"]
        if User.all_objects.filter(email=value).exclude(pk=current_user.pk).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверить, что хотя бы одно поле передано в запросе."""
        if not attrs:
            raise serializers.ValidationError("Не переданы данные для обновления.")
        return attrs
