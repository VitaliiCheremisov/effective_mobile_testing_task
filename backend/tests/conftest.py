import pytest
from rest_framework.test import APIClient

from apps.core.models import Permission, Role, RolePermission, User


@pytest.fixture
def client():
    """Возвращает неаутентифицированный DRF APIClient."""
    return APIClient()


@pytest.fixture
def make_user():
    """Фабрика для создания тестовых пользователей.

    Использование: user = make_user(email="...", password="...", is_active=True)
    """

    def _make(
        email: str = "user@example.com",
        password: str = "StrongPass123!",
        full_name: str = "Test User",
        is_active: bool = True,
    ) -> User:
        user = User.all_objects.create(
            full_name=full_name, email=email, is_active=is_active
        )
        user.set_password(password)
        user.save(update_fields=["password_hash"])
        return user

    return _make


@pytest.fixture
def make_role():
    """Фабрика для создания ролей с набором прав.

    Использование: role = make_role("manager", "can_view_reports")
    """

    def _make(name: str, *permission_codenames: str) -> Role:
        role, _ = Role.objects.get_or_create(name=name)
        for codename in permission_codenames:
            perm, _ = Permission.objects.get_or_create(
                codename=codename, defaults={"name": codename}
            )
            RolePermission.objects.get_or_create(role=role, permission=perm)
        return role

    return _make


@pytest.fixture
def auth_client(client, make_user):
    """APIClient с JWT-токеном активного пользователя.

    Возвращает кортеж (client, user, token).
    """
    user = make_user()
    resp = client.post(
        "/api/v1/auth/login/",
        {"email": "user@example.com", "password": "StrongPass123!"},
    )
    token = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client, user, token
