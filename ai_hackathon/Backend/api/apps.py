"""App configuration for the generic API wrapper."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Register the generic API app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
