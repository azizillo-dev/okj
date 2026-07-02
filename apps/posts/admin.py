"""
OKJ PLATFORM - POSTS ADMIN PANEL (apps/posts/admin.py)
Nega bu fayl kerak: Boshqaruv paneli orqali postlarni moderatsiya qilish,
shikoyatlarni tekshirish va rasmlarni ko'rish.
"""

from django.contrib import admin
from .models import Post, PostMedia, PostReport, DraftPost, PostViewCounter


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "post_type", "status", "moderation_status", "visibility", "published_at", "views_count")
    list_filter = ("post_type", "status", "moderation_status", "visibility")
    search_fields = ("user__username", "title", "content", "hashtags")
    autocomplete_fields = ("user", "book", "district", "library_item")
    readonly_fields = ("id", "slug", "views_count", "created_at", "updated_at")
    inlines = [PostMediaInline]
    actions = ["approve_posts", "reject_posts"]

    @admin.action(description="Tanlangan postlarni tasdiqlash (APPROVED)")
    def approve_posts(self, request, queryset):
        queryset.update(moderation_status=Post.ModerationStatus.APPROVED)

    @admin.action(description="Tanlangan postlarni rad etish (REJECTED)")
    def reject_posts(self, request, queryset):
        queryset.update(moderation_status=Post.ModerationStatus.REJECTED)


@admin.register(DraftPost)
class DraftPostAdmin(admin.ModelAdmin):
    list_display = ("user", "post_type", "title", "updated_at")
    list_filter = ("post_type",)
    search_fields = ("user__username", "title", "content")


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "reason", "is_resolved", "created_at")
    list_filter = ("is_resolved", "reason")
    search_fields = ("user__username", "post__id", "details")
    readonly_fields = ("id", "post", "user", "reason", "details", "is_resolved", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PostViewCounter)
class PostViewCounterAdmin(admin.ModelAdmin):
    list_display = ("post", "total_views", "unique_views")
    readonly_fields = ("created_at", "updated_at")
