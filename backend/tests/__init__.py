import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "DATABASE_URL", "postgres://postgres:postgres@localhost:5432/postgres"
    ),
)
os.environ.setdefault(
    "JWT_SECRET_KEY", os.environ.get("JWT_SECRET_KEY", "test-secret-key")
)

django.setup()
