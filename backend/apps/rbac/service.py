from __future__ import annotations

from apps.core.models import User


def has_permission(user: User, codename: str) -> bool:
    """Проверить, есть ли у пользователя право с указанным кодом.

    Алгоритм: пользователь → его роли → права ролей → поиск codename.
    """
    return user.user_roles.filter(
        role__role_permissions__permission__codename=codename,
    ).exists()
