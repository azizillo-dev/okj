"""
OKJ PLATFORM - AUTHENTICATION APP CONFIGURATION
Nega bu fayl kerak: Authentication appni ro'yxatdan o'tkazish va ishga tushganda 
signals.py dagi hodisalarni ulab qo'yish.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    verbose_name = "OKJ Security, Auth & Sessions"

    def ready(self):
        import authentication.signals  # noqa
