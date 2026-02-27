from django.urls import include, path

from config import views
from apps.users.views import DeleteMeView, LoginView, LogoutView, MeView, RegisterView


urlpatterns = [
    path("api/v1/health/", views.health),
    path("api/v1/auth/register/", RegisterView.as_view(), name="auth-register"),
    path("api/v1/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/v1/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/v1/users/me/", MeView.as_view(), name="users-me"),
    path("api/v1/users/me/delete/", DeleteMeView.as_view(), name="users-me-delete"),
    path("api/admin/", include("apps.rbac.urls")),
    path("api/v1/", include("apps.business.urls")),
]
