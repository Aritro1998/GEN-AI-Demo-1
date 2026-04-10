"""DRF serializers for the insurance policy query API."""

from rest_framework import serializers

from api.models import PolicyCategory, PolicyTier, UserPolicy


class ChatMessageSerializer(serializers.Serializer):
    """A single message in the conversation history."""

    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()


class PolicyQuerySerializer(serializers.Serializer):
    """Validate an insurance policy question with optional chat history."""

    question = serializers.CharField()
    user_policy_id = serializers.IntegerField(required=False, default=None)
    chat_history = ChatMessageSerializer(many=True, required=False, default=[])


class PolicyUploadSerializer(serializers.Serializer):
    """Validate admin policy PDF upload — requires a tier to attach to."""

    tier_id = serializers.IntegerField()
    file = serializers.FileField()

    def validate_tier_id(self, value):
        if not PolicyTier.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"PolicyTier with id={value} not found.")
        return value

    def validate_file(self, value):
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are supported.")
        return value


class UserPolicyAssignSerializer(serializers.Serializer):
    """Assign a policy tier to a user."""

    user_id = serializers.IntegerField()
    tier_id = serializers.IntegerField()
    policy_number = serializers.CharField(max_length=50)
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class PolicyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyCategory
        fields = ["id", "name", "description", "icon"]


class PolicyTierSerializer(serializers.ModelSerializer):
    category = PolicyCategorySerializer(read_only=True)

    class Meta:
        model = PolicyTier
        fields = ["id", "category", "name", "display_name", "price_monthly", "highlights"]


class UserPolicySerializer(serializers.ModelSerializer):
    tier = PolicyTierSerializer(read_only=True)
    has_document = serializers.SerializerMethodField()

    class Meta:
        model = UserPolicy
        fields = ["id", "tier", "policy_number", "start_date", "end_date", "is_active", "has_document"]

    def get_has_document(self, obj):
        from api.models import PolicyDocument
        return PolicyDocument.objects.filter(
            tier=obj.tier, pdf_file__isnull=False,
        ).exclude(pdf_file="").exists()
