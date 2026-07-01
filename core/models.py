"""
OKJ PLATFORM - CORE ABSTRACT MODELS (core/models.py)
Nega bu fayl kerak: Barcha biznes modullari (accounts, books, posts) kodni takrorlamasdan
yagona standartdagi UUID, sana loglari va Soft Delete imkoniyatlaridan foydalanishi uchun.
"""

import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Barcha jadvallarda yaratilgan va oxirgi o'zgartirilgan vaqtni avtomat saqlaydi.
    Nega db_index=True: Lenta va qidiruvlarda vaqt bo'yicha saralash (ORDER BY created_at DESC) juda tez ishlashi uchun.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Tashqi dunyoga ko'rinadigan obyektlar (User, Book, Post) uchun UUIDv4 Primary Key.
    Nega UUID: URL orqali ketma-ket raqamlarni taxmin qilishni (ID Enumeration Attack) to'xtatish uchun.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Faqat o'chirilmagan (is_deleted=False) obyektlarni qaytaruvchi menedjer."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    O'chirilganda bazadan fiziki yo'qolmaydigan, faqat is_deleted bayrog'i yoqiladigan model.
    Nega kerak: Foydalanuvchi postni o'chirsa, unga bog'liq tarixiy almashinuvlar buzilmasligi uchun.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        """Soft delete amalini bajarish."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Haqiqiy fiziki o'chirish."""
        return super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True
