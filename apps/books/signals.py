"""
OKJ PLATFORM - BOOKS SIGNALS (apps/books/signals.py)
Nega bu fayl kerak: Kitoblar saqlanganda kashlarni tozalash yoki
statistika jadvallarini avtomat sinxronizatsiya qilish.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, BookStatistics

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Book)
def ensure_book_statistics_exists(sender, instance: Book, created: bool, **kwargs):
    """Kitob yaratilsa, uning statistika jadvali bo'lishini kafolatlash."""
    if created:
        BookStatistics.objects.get_or_create(book=instance)
        logger.info(f"Katalogga yangi kitob qo'shildi: {instance.title} ({instance.isbn_13 or 'No ISBN'})")
