from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.rbac import service as rbac_service


class RBACPermission(BasePermission):
    """Базовый класс разрешений для RBAC.

    Использование:
    - required_permission = None — достаточно факта аутентификации.
    - required_permission = "<codename>" — проверяется конкретное право.
    """

    required_permission: str | None = None

    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        """Проверить, есть ли у пользователя доступ к ресурсу.

        Если пользователь не аутентифицирован — вернуть False (→ 401).
        Если required_permission задан — проверить наличие права (→ 403 при отсутствии).
        """
        if not request.user or not request.user.is_authenticated:
            self.message = "Учётные данные не предоставлены."
            return False

        if self.required_permission is None:
            return True

        result = rbac_service.has_permission(
            request.user,  # type: ignore[arg-type]
            self.required_permission,
        )
        if not result:
            self.message = "Недостаточно прав для выполнения операции."
        return result
