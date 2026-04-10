"""Endpoint definitions for the insurance policy provider API."""

from django.urls import path

from api.auth_views import CurrentUserView, LoginView, LogoutView
from api.views import (
    DashboardView,
    HealthCheckView,
    MyPoliciesView,
    OfferingsView,
    PolicyDetailView,
    PolicyDocumentDownloadView,
    PolicyQueryView,
    PolicyUploadView,
    RecommendationsView,
    ScopedPolicyQueryView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    # Auth
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    # User-facing
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("my-policies/", MyPoliciesView.as_view(), name="my-policies"),
    path("my-policies/<int:policy_id>/", PolicyDetailView.as_view(), name="policy-detail"),
    path("my-policies/<int:policy_id>/document/", PolicyDocumentDownloadView.as_view(), name="policy-document"),
    path("my-policies/<int:policy_id>/query/", ScopedPolicyQueryView.as_view(), name="scoped-policy-query"),
    path("recommendations/", RecommendationsView.as_view(), name="recommendations"),
    path("offerings/", OfferingsView.as_view(), name="offerings"),
    path("query/", PolicyQueryView.as_view(), name="policy-query"),
    # Admin-only
    path("upload-policy/", PolicyUploadView.as_view(), name="policy-upload"),
]
