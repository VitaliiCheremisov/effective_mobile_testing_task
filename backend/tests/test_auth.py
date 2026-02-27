import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_ok():
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/register/",
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "SecurePass1!",
            "password_confirm": "SecurePass1!",
        },
    )
    assert resp.status_code == 201
    assert resp.data["email"] == "jane@example.com"


@pytest.mark.django_db
def test_login_ok(make_user):
    make_user(email="alice@example.com", password="StrongPass123!")
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/login/",
        {"email": "alice@example.com", "password": "StrongPass123!"},
    )
    assert resp.status_code == 200
    assert "access" in resp.data


@pytest.mark.django_db
def test_login_soft_deleted_user(make_user):
    """Soft-deleted user (is_active=False) must not be able to log in."""
    make_user(email="deleted@example.com", password="StrongPass123!", is_active=False)
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/login/",
        {"email": "deleted@example.com", "password": "StrongPass123!"},
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_token_blacklist(make_user):
    """After logout the same token must be rejected with 401."""
    make_user(email="bob@example.com", password="StrongPass123!")
    client = APIClient()

    login_resp = client.post(
        "/api/v1/auth/login/",
        {"email": "bob@example.com", "password": "StrongPass123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    logout_resp = client.post("/api/v1/auth/logout/")
    assert logout_resp.status_code == 204

    profile_resp = client.get("/api/v1/users/me/")
    assert profile_resp.status_code == 401
