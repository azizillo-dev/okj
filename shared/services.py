"""
OKJ PLATFORM - BASE SERVICE CLASSES (shared/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide me'morchiligida BARCHA YOZISH (INSERT/UPDATE/DELETE)
amalari faqat `services.py` ichida bo'lishi shart. Bu yerdagi klasslar ularga tranzaksiya
qoidalari va validatsiyani avtomat ulaydi.
"""

from typing import Any
from django.db import transaction


class BaseService:
    """
    Barcha servislar uchun poydevor.
    Biron bir servisni bajarishda agar xato kelsa tranzaksiyani avtomat orqaga qaytaradi (rollback).
    """
    @classmethod
    @transaction.atomic
    def execute(cls, *args, **kwargs) -> Any:
        raise NotImplementedError("Servis ichida execute() metodi yozilishi shart.")
