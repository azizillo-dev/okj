"""
OKJ PLATFORM - NOTIFICATIONS ADMIN PANEL (apps/notifications/admin.py)
"""

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("recipient__username", "actor__username", "text")
    autocomplete_fields = ("recipient", "actor")
