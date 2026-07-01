"""
OKJ PLATFORM - POSTS APP CONFIGURATION
Nega bu fayl kerak: Posts appni ro'yxatdan o'tkazish va ishga tushganda 
signals.py dagi hodisalarni ulab qo'yish.
"""

from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "posts"
    verbose_name = "OKJ Social Feed & Reader Posts"

    def ready(self):
        import posts.signals  # noqa
