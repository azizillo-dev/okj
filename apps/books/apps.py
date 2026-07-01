"""
OKJ PLATFORM - BOOKS APP CONFIGURATION
Nega bu fayl kerak: Books appni ro'yxatdan o'tkazish va ishga tushganda 
signals.py dagi hodisalarni (receiverlarni) ulab qo'yish.
"""

from django.apps import AppConfig


class BooksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "books"
    verbose_name = "OKJ Books & Global Library Catalog"

    def ready(self):
        import books.signals  # noqa
