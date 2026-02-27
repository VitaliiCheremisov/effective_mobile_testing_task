from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Permission, Role, RolePermission, User, UserRole
from apps.rbac.permissions import RBACPermission
from apps.rbac.serializers import (
    AddPermissionToRoleSerializer,
    AssignRoleToUserSerializer,
    PermissionSerializer,
    RoleCreateSerializer,
    RoleSerializer,
)


class AdminRequiredPermission(RBACPermission):
    """Разрешение только для пользователей с правом can_manage_roles."""

    required_permission = "can_manage_roles"


class RoleListCreateView(APIView):
    """Список и создание ролей.

    GET  /api/admin/roles/ — получить все роли.
    POST /api/admin/roles/ — создать новую роль.
    Требует права can_manage_roles.
    """

    permission_classes = [AdminRequiredPermission]

    def get(self, request: Request) -> Response:
        """Вернуть список всех ролей."""
        roles = Role.objects.all()
        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request: Request) -> Response:
        """Создать новую роль."""
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role = Role.objects.create(
            name=data["name"],
            description=data.get("description", ""),
        )
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    """Детали и удаление роли.

    GET    /api/admin/roles/{id}/ — получить роль.
    DELETE /api/admin/roles/{id}/ — удалить роль.
    Требует права can_manage_roles.
    """

    permission_classes = [AdminRequiredPermission]

    def _get_role(self, pk: int) -> Role:
        """Получить роль по pk или вернуть 404."""
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            raise NotFound("Роль не найдена.")

    def get(self, request: Request, pk: int) -> Response:
        """Вернуть данные роли."""
        role = self._get_role(pk)
        return Response(RoleSerializer(role).data)

    def delete(self, request: Request, pk: int) -> Response:
        """Удалить роль."""
        role = self._get_role(pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PermissionListView(APIView):
    """Список всех прав доступа.

    GET /api/admin/permissions/ — получить все права.
    Требует права can_manage_roles.
    """

    permission_classes = [AdminRequiredPermission]

    def get(self, request: Request) -> Response:
        """Вернуть список всех прав доступа."""
        permissions = Permission.objects.all()
        return Response(PermissionSerializer(permissions, many=True).data)


class RolePermissionView(APIView):
    """Управление правами роли.

    POST   /api/admin/roles/{id}/permissions/           — добавить право роли.
    DELETE /api/admin/roles/{id}/permissions/{perm_id}/ — убрать право у роли.
    Требует права can_manage_roles.
    """

    permission_classes = [AdminRequiredPermission]

    def _get_role(self, pk: int) -> Role:
        """Получить роль по pk или вернуть 404."""
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            raise NotFound("Роль не найдена.")

    def post(self, request: Request, pk: int) -> Response:
        """Назначить право роли."""
        role = self._get_role(pk)
        serializer = AddPermissionToRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission_id = serializer.validated_data["permission_id"]
        permission = Permission.objects.get(pk=permission_id)

        _, created = RolePermission.objects.get_or_create(
            role=role, permission=permission
        )
        if not created:
            raise ValidationError("Это право уже назначено данной роли.")

        return Response(
            {
                "detail": f"Право '{permission.codename}' добавлено к роли '{role.name}'."
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request: Request, pk: int, perm_id: int) -> Response:
        """Снять право у роли."""
        role = self._get_role(pk)
        try:
            rp = RolePermission.objects.get(role=role, permission_id=perm_id)
        except RolePermission.DoesNotExist:
            raise NotFound("Это право не назначено данной роли.")
        rp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleView(APIView):
    """Управление ролями пользователя.

    POST   /api/admin/users/{id}/roles/            — назначить роль пользователю.
    DELETE /api/admin/users/{id}/roles/{role_id}/ — снять роль с пользователя.
    Требует права can_manage_roles.
    """

    permission_classes = [AdminRequiredPermission]

    def _get_user(self, pk: int) -> User:
        """Получить пользователя по pk или вернуть 404."""
        try:
            return User.all_objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден.")

    def post(self, request: Request, pk: int) -> Response:
        """Назначить роль пользователю."""
        user = self._get_user(pk)
        serializer = AssignRoleToUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_id = serializer.validated_data["role_id"]
        role = Role.objects.get(pk=role_id)

        _, created = UserRole.objects.get_or_create(user=user, role=role)
        if not created:
            raise ValidationError("Эта роль уже назначена пользователю.")

        return Response(
            {"detail": f"Роль '{role.name}' назначена пользователю '{user.email}'."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request: Request, pk: int, role_id: int) -> Response:
        """Снять роль с пользователя."""
        user = self._get_user(pk)
        try:
            ur = UserRole.objects.get(user=user, role_id=role_id)
        except UserRole.DoesNotExist:
            raise NotFound("Эта роль не назначена пользователю.")
        ur.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
