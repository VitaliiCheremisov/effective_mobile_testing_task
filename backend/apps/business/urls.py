from django.urls import path

from apps.business import views

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="business-profile"),
    path("reports/", views.ReportsView.as_view(), name="business-reports"),
    path("admin/stats/", views.AdminStatsView.as_view(), name="business-admin-stats"),
]
