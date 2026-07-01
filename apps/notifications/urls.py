"""
OKJ PLATFORM - NOTIFICATIONS URLS (apps/notifications/urls.py)
Nega bu fayl kerak: /api/v1/notifications/ marshrutlari.
"""

from django.urls import path
from .apis import NotificationInboxApi, UnreadCountApi, MarkAsReadApi, MarkAllAsReadApi

urlpatterns = [
    path("", NotificationInboxApi.as_view(), name="notification-inbox"),
    path("unread-count/", UnreadCountApi.as_view(), name="notification-unread-count"),
    path("read-all/", MarkAllAsReadApi.as_view(), name="notification-read-all"),
    path("<str:notification_id>/read/", MarkAsReadApi.as_view(), name="notification-mark-read"),
]
