"""
OKJ PLATFORM - BOOKS MANAGERS (apps/books/managers.py)
Nega bu fayl kerak: Qidiruv va kataloglarda faqat tasdiqlangan (`VERIFIED`)
va o'chirilmagan kitoblar ko'rinishini avtomatik ta'minlovchi menejerlar.
"""

from django.db import models


class ActiveBookManager(models.Manager):
    """Faqat o'chirilmagan (is_deleted=False) kitoblar ro'yxati."""
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)


class VerifiedBookManager(models.Manager):
    """
    Standart qidiruvlar uchun: faqat kurator tomonidan tasdiqlangan (VERIFIED) 
    va o'chirilmagan kitoblar ro'yxati.
    """
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False, verification_status="VERIFIED")
