"""
OKJ PLATFORM - FOLLOWS APP CONFIGURATION
Nega bu fayl kerak: Follows (Obunalar va Ijtimoiy Graf) appni ro'yxatdan o'tkazish.
"""

from django.apps import AppConfig


class FollowsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "follows"
    verbose_name = "OKJ Social Graph & Follows"
