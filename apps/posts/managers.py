"""
OKJ PLATFORM - POSTS MANAGERS (apps/posts/managers.py)
Nega bu fayl kerak: Faqat tasdiqlangan va chop etilgan postlarni yoki
qoralamalarni avtomatik ajratib berish.
"""

from django.db import models


class ActivePostManager(models.Manager):
    """Faqat o'chirilmagan (Soft Delete qilinmagan) postlar."""
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)


class PublishedPostManager(models.Manager):
    """Faqat chop etilgan va moderatsiyadan o'tgan (APPROVED) postlar."""
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(
            is_deleted=False,
            status="PUBLISHED",
            moderation_status="APPROVED",
        )


class DraftPostManager(models.Manager):
    """Faqat qoralama (DRAFT) holatidagi postlar."""
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False, status="DRAFT")
