"""DRF serializers for generic API request validation."""

from rest_framework import serializers


class KnowledgeEntrySerializer(serializers.Serializer):
    """Validate a manual knowledge entry before writing it to disk."""

    title = serializers.CharField(max_length=200)
    summary = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField(max_length=50, default="Others")
    notes = serializers.CharField(allow_blank=True, required=False, default="")
    source = serializers.CharField(max_length=50, required=False, default="manual")


class PromoteKnowledgeSerializer(serializers.Serializer):
    """Validate payloads that promote a reviewed output into the knowledge base."""

    title = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    summary = serializers.CharField(required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    category = serializers.CharField(max_length=50, required=False, default="Others")
    notes = serializers.CharField(allow_blank=True, required=False, default="")
    source = serializers.CharField(max_length=50, required=False, default="promoted_output")
    final_output = serializers.CharField(required=False, allow_blank=True, default="")
    analysis = serializers.CharField(required=False, allow_blank=True, default="")
    classification = serializers.CharField(required=False, allow_blank=True, default="")
    original_input = serializers.CharField(required=False, allow_blank=True, default="")
    auto_format = serializers.BooleanField(required=False, default=False)
