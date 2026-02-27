import pytest
from rest_framework.test import APIClient

from apps.core.models import UserRole


@pytest.mark.django_db
def test_profile_requires_auth():
    """Request without a token must return 401."""
    client = APIClient()
    resp = client.get("/api/v1/profile/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_profile_authenticated(auth_client):
    """Authenticated user can access their profile."""
    client, user, _ = auth_client
    resp = client.get("/api/v1/profile/")
    assert resp.status_code == 200
    assert resp.data["data"]["email"] == user.email


@pytest.mark.django_db
def test_access_forbidden(auth_client):
    """Regular user without any roles must get 403 on a permission-protected endpoint."""
    client, user, _ = auth_client
    resp = client.get("/api/v1/reports/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_reports_with_permission(make_user, make_role):
    """User with can_view_reports role can access /reports/."""
    user = make_user(email="manager@example.com", password="StrongPass123!")
    role = make_role("manager", "can_view_reports")
    UserRole.objects.create(user=user, role=role)

    client = APIClient()
    login_resp = client.post(
        "/api/v1/auth/login/",
        {"email": "manager@example.com", "password": "StrongPass123!"},
    )
    token = login_resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = client.get("/api/v1/reports/")
    assert resp.status_code == 200
    assert resp.data["resource"] == "reports"
