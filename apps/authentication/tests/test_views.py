import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def _login(client, email="jane@example.com", password="strong-pass-123"):
    UserFactory(email=email, password=password)
    return client.post("/api/v1/auth/login/", {"email": email, "password": password})


def test_login_returns_access_token_and_sets_refresh_cookie():
    client = APIClient()
    response = _login(client)

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data

    cookie = response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME]
    assert cookie.value
    assert cookie["httponly"]


def test_login_with_wrong_password_fails():
    client = APIClient()
    UserFactory(email="jane@example.com", password="correct-pass")
    response = client.post(
        "/api/v1/auth/login/", {"email": "jane@example.com", "password": "wrong-pass"}
    )
    assert response.status_code == 401
    assert response.data["success"] is False


def test_refresh_without_cookie_returns_401():
    client = APIClient()
    response = client.post("/api/v1/auth/refresh/")
    assert response.status_code == 401


def test_refresh_with_valid_cookie_returns_new_access_token():
    client = APIClient()
    login_response = _login(client)
    refresh_cookie = login_response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME].value

    client.cookies[settings.REFRESH_TOKEN_COOKIE_NAME] = refresh_cookie
    response = client.post("/api/v1/auth/refresh/")

    assert response.status_code == 200
    assert "access" in response.data


def test_me_requires_authentication():
    client = APIClient()
    response = client.get("/api/v1/auth/me/")
    assert response.status_code == 401


def test_me_returns_current_user():
    user = UserFactory(email="jane@example.com")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.data["email"] == "jane@example.com"


def test_logout_clears_refresh_cookie():
    client = APIClient()
    response = client.post("/api/v1/auth/logout/")
    assert response.status_code == 204
    cookie = response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME]
    assert cookie.value == ""
