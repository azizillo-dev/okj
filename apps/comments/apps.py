"""
OKJ PLATFORM - COMMENTS APP CONFIGURATION
Nega bu fayl kerak: Comments (Izohlar va Muhokamalar) appni ro'yxatdan o'tkazish.
"""

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "comments"
    verbose_name = "OKJ Post Comments & Discussions"
