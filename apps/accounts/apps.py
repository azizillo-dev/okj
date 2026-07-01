"""
OKJ PLATFORM - ACCOUNTS APP CONFIGURATION
Nega bu fayl kerak: Django appni ro'yxatdan o'tkazish va ishga tushganda 
signals.py dagi hodisalarni (receiverlarni) ulab qo'yish uchun.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "OKJ Accounts & Reader Identity"

    def ready(self):
        # App ishga tushganda signallarni ulaymiz
        import accounts.signals  # noqa
