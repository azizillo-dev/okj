"""
OKJ PLATFORM - INTERACTIONS APP CONFIGURATION
Nega bu fayl kerak: Interactions (Layk va Bookmark) appni ro'yxatdan o'tkazish.
"""

from django.apps import AppConfig


class InteractionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "interactions"
    verbose_name = "OKJ Post Likes & Bookmarks"
