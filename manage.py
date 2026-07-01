#!/usr/bin/env python
"""
OKJ Platformasi - Django'ning interaktiv buyruqlarni boshqaruvchi fayli.
Nega bu fayl kerak: Barcha buyruqlar (migrate, runserver, shell) orqali sozlamalarni 
'config.settings.local' ga standart yuborishni ta'minlaydi.
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
