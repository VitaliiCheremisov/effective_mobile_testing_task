"""
Django settings for auth RBAC backend.
DB and secrets берутся из переменных окружения (без django-environ, чтобы не
зависеть от дополнительного пакета внутри контейнера).
"""

import os
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DEBUG = _get_bool_env("DEBUG", False)
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "config",
    "apps.core",  # текущие доменные модели (User, Role, Permission, Blacklist)
    "apps.users",  # пользовательский API (регистрация, профиль) — планируется
    "apps.auth_core",  # JWT‑аутентификация и blacklist — планируется
    "apps.rbac",  # RBAC‑правила и permission‑классы — планируется
    "apps.business",  # mock‑ресурсы для демонстрации прав — планируется
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

_database_url = os.environ.get(
    "DATABASE_URL",
    "postgres://postgres:postgres@localhost:5432/postgres",
)
_parsed_db = urlparse(_database_url)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _parsed_db.path.lstrip("/") or "postgres",
        "USER": _parsed_db.username or "postgres",
        "PASSWORD": _parsed_db.password or "postgres",
        "HOST": _parsed_db.hostname or "localhost",
        "PORT": str(_parsed_db.port or 5432),
    }
}

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.auth_core.backends.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.rbac.permissions.RBACPermission",
    ],
    # django.contrib.auth is not installed; tell DRF not to use AnonymousUser.
    "UNAUTHENTICATED_USER": None,
}
