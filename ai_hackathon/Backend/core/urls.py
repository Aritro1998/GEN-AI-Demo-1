"""Root URL configuration for the hackathon API project."""

from django.urls import include, path

urlpatterns = [
    path("api/", include("api.urls")),
]
