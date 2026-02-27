from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.core.models import Permission, Role


class RoleSerializer(serializers.ModelSerializer[Role]):
    """Сериализатор для представления роли."""

    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class PermissionSerializer(serializers.ModelSerializer[Permission]):
    """Сериализатор для представления права доступа."""

    class Meta:
        model = Permission
        fields = ["id", "codename", "name"]


class RoleCreateSerializer(serializers.Serializer[dict[str, Any]]):
    """Валидация данных при создании новой роли."""

    name = serializers.CharField(max_length=64)
    description = serializers.CharField(required=False, default="", allow_blank=True)

    def validate_name(self, value: str) -> str:
        """Проверить уникальность имени роли."""
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("Роль с таким именем уже существует.")
        return value


class AddPermissionToRoleSerializer(serializers.Serializer[dict[str, Any]]):
    """Валидация данных при добавлении права к роли."""

    permission_id = serializers.IntegerField()

    def validate_permission_id(self, value: int) -> int:
        """Проверить, что право с указанным id существует."""
        if not Permission.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Право доступа не найдено.")
        return value


class AssignRoleToUserSerializer(serializers.Serializer[dict[str, Any]]):
    """Валидация данных при назначении роли пользователю."""

    role_id = serializers.IntegerField()

    def validate_role_id(self, value: int) -> int:
        """Проверить, что роль с указанным id существует."""
        if not Role.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Роль не найдена.")
        return value
