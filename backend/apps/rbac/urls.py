from django.urls import path

from apps.rbac import views

urlpatterns = [
    path("roles/", views.RoleListCreateView.as_view(), name="admin-role-list"),
    path("roles/<int:pk>/", views.RoleDetailView.as_view(), name="admin-role-detail"),
    path(
        "permissions/", views.PermissionListView.as_view(), name="admin-permission-list"
    ),
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
