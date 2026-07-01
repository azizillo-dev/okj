"""
OKJ PLATFORM - BASE SELECTOR CLASSES (shared/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide me'morchiligida BARCHA O'QISH (SELECT)
amallari faqat `selectors.py` ichida bo'lishi shart. Bu viewlar ichida og'ir ORM
so'rovlar yozilmasligini kafolatlaydi.
"""

from typing import Any
from django.db.models import QuerySet


class BaseSelector:
    """
    Barcha selektorlar uchun poydevor.
    """
    @classmethod
    def get_queryset(cls, *args, **kwargs) -> QuerySet:
        raise NotImplementedError("Selector ichida get_queryset() metodi yozilishi shart.")
