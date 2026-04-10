"""Domain models for the insurance policy provider platform."""

from django.conf import settings
from django.db import models


class PolicyCategory(models.Model):
    """Top-level policy type such as Car, Health, Life, Home."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Optional icon identifier for the frontend (e.g. 'car', 'health').",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "policy categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PolicyTier(models.Model):
    """A tier within a category — e.g. Silver, Gold, Platinum."""

    TIER_CHOICES = [
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
    ]

    category = models.ForeignKey(
        PolicyCategory, on_delete=models.CASCADE, related_name="tiers",
    )
    name = models.CharField(max_length=50, choices=TIER_CHOICES)
    display_name = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Human-friendly label, e.g. 'Gold Motor Cover'.",
    )
    price_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Indicative monthly premium for recommendation comparisons.",
    )
    highlights = models.TextField(
        blank=True, default="",
        help_text="Short bullet-point summary of what this tier offers.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("category", "name")
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.category.name} — {self.get_name_display()}"


class PolicyDocument(models.Model):
    """A PDF document attached to a specific category + tier."""

    tier = models.ForeignKey(
        PolicyTier, on_delete=models.CASCADE, related_name="documents",
    )
    file_name = models.CharField(max_length=255)
    pdf_file = models.FileField(
        upload_to="policy_pdfs/", blank=True, null=True,
        help_text="Stored copy of the uploaded PDF.",
    )
    page_count = models.PositiveIntegerField(default=0)
    chunk_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.file_name} ({self.tier})"


class PolicyChunk(models.Model):
    """An individual text chunk extracted from a policy document."""

    document = models.ForeignKey(
        PolicyDocument, on_delete=models.CASCADE, related_name="chunks",
    )
    chunk_index = models.PositiveIntegerField()
    page = models.PositiveIntegerField()
    text = models.TextField()

    class Meta:
        ordering = ["document", "chunk_index"]
        unique_together = ("document", "chunk_index")

    def __str__(self):
        return f"{self.document.file_name} chunk {self.chunk_index}"


class UserPolicy(models.Model):
    """Links a user to a specific policy tier — one per category per user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="policies",
    )
    tier = models.ForeignKey(
        PolicyTier, on_delete=models.CASCADE, related_name="subscribers",
    )
    policy_number = models.CharField(
        max_length=50, unique=True,
        help_text="Unique policy reference number.",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "user policies"
        unique_together = ("user", "tier")
        ordering = ["user", "tier__category"]

    def __str__(self):
        return f"{self.user.username} — {self.tier} ({self.policy_number})"
