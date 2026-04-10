"""Admin panel registration for the insurance policy platform models."""

from django.contrib import admin

from api.models import (
    PolicyCategory,
    PolicyChunk,
    PolicyDocument,
    PolicyTier,
    UserPolicy,
)


@admin.register(PolicyCategory)
class PolicyCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


class PolicyDocumentInline(admin.TabularInline):
    model = PolicyDocument
    extra = 0
    readonly_fields = ("file_name", "page_count", "chunk_count", "uploaded_at")


@admin.register(PolicyTier)
class PolicyTierAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "display_name", "price_monthly", "created_at")
    list_filter = ("category", "name")
    search_fields = ("display_name",)
    inlines = [PolicyDocumentInline]


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "tier", "page_count", "chunk_count", "uploaded_at")
    list_filter = ("tier__category", "tier__name")
    readonly_fields = ("page_count", "chunk_count", "uploaded_at")


@admin.register(PolicyChunk)
class PolicyChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "page", "short_text")
    list_filter = ("document__tier__category",)
    search_fields = ("text",)

    def short_text(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    short_text.short_description = "Text preview"


@admin.register(UserPolicy)
class UserPolicyAdmin(admin.ModelAdmin):
    list_display = ("user", "tier", "policy_number", "start_date", "end_date", "is_active")
    list_filter = ("tier__category", "tier__name", "is_active")
    search_fields = ("user__username", "policy_number")
