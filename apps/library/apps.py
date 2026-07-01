"""
OKJ PLATFORM - LIBRARY APP CONFIGURATION
Nega bu fayl kerak: Library appni ro'yxatdan o'tkazish va ishga tushganda 
signals.py dagi hodisalarni ulab qo'yish.
"""

from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "library"
    verbose_name = "OKJ Personal Library & Reading Progress"

    def ready(self):
        import library.signals  # noqa
