"""
OKJ PLATFORM - INTERACTIONS ADMIN PANEL (apps/interactions/admin.py)
"""

from django.contrib import admin
from .models import PostLike, PostBookmark


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "is_deleted", "created_at")
    list_filter = ("is_deleted", "created_at")
    search_fields = ("user__username", "post__id")
    autocomplete_fields = ("user", "post")


@admin.register(PostBookmark)
class PostBookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "collection_name", "is_deleted", "created_at")
    list_filter = ("collection_name", "is_deleted")
    search_fields = ("user__username", "post__id", "collection_name")
    autocomplete_fields = ("user", "post")
