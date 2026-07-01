"""
OKJ PLATFORM - NOTIFICATIONS APP CONFIGURATION
Nega bu fayl kerak: Notifications (Markazlashgan Asinxron Bildirishnomalar) appni ro'yxatdan o'tkazish.
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "OKJ Asynchronous Notifications"
