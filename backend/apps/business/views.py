from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.permissions import RBACPermission


class ReportsPermission(RBACPermission):
    """Разрешение для доступа к отчётам. Требует право can_view_reports."""

    required_permission = "can_view_reports"


class AdminStatsPermission(RBACPermission):
    """Разрешение для доступа к статистике. Требует право can_view_stats."""

    required_permission = "can_view_stats"


class ProfileView(APIView):
    """Профиль текущего пользователя. Доступен любому аутентифицированному."""

    permission_classes = [RBACPermission]

    def get(self, request: Request) -> Response:
        """Вернуть базовые данные текущего пользователя."""
        user = request.user
        return Response(
            {
                "resource": "profile",
                "data": {
                    "id": user.pk,
                    "email": getattr(user, "email", None),
                    "full_name": getattr(user, "full_name", None),
                },
            }
        )


class ReportsView(APIView):
    """Демонстрационный ресурс «Отчёты». Требует право can_view_reports."""

    permission_classes = [ReportsPermission]

    def get(self, request: Request) -> Response:
        """Вернуть заглушку данных отчётов."""
        return Response({"resource": "reports", "data": "Secret reports"})


class AdminStatsView(APIView):
    """Демонстрационный ресурс «Статистика». Требует право can_view_stats."""

    permission_classes = [AdminStatsPermission]

    def get(self, request: Request) -> Response:
        """Вернуть заглушку административной статистики."""
        return Response({"resource": "admin_stats", "data": "Top secret"})
