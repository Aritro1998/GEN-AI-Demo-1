"""Endpoint definitions for the generic multimodal API."""

from django.urls import path

from api.views import (
    HealthCheckView,
    KnowledgeEntryCreateView,
    KnowledgePromoteView,
    ProcessRequestView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("process/", ProcessRequestView.as_view(), name="process-request"),
    path("knowledge/", KnowledgeEntryCreateView.as_view(), name="knowledge-create"),
    path("knowledge/promote/", KnowledgePromoteView.as_view(), name="knowledge-promote"),
]
