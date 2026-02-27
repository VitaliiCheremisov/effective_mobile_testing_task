from django.urls import path

from apps.rbac import views

urlpatterns = [
    # Roles CRUD
    path("roles/", views.RoleListCreateView.as_view(), name="admin-role-list"),
    path("roles/<int:pk>/", views.RoleDetailView.as_view(), name="admin-role-detail"),
    # Permissions list (read-only; permissions are seeded via migrations/fixtures)
    path(
        "permissions/", views.PermissionListView.as_view(), name="admin-permission-list"
    ),
    # Role ↔ Permission management
    path(
        "roles/<int:pk>/permissions/",
        views.RolePermissionView.as_view(),
        name="admin-role-permission-add",
    ),
    path(
        "roles/<int:pk>/permissions/<int:perm_id>/",
        views.RolePermissionView.as_view(),
        name="admin-role-permission-remove",
    ),
    # User ↔ Role management
    path(
        "users/<int:pk>/roles/",
        views.UserRoleView.as_view(),
        name="admin-user-role-assign",
    ),
    path(
        "users/<int:pk>/roles/<int:role_id>/",
        views.UserRoleView.as_view(),
        name="admin-user-role-remove",
    ),
]
