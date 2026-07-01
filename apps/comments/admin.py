"""
OKJ PLATFORM - COMMENTS ADMIN PANEL (apps/comments/admin.py)
"""

from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "parent", "is_approved", "is_deleted", "created_at")
    list_filter = ("is_approved", "is_deleted", "created_at")
    search_fields = ("user__username", "text", "post__id")
    autocomplete_fields = ("user", "post", "parent")
