"""
OKJ PLATFORM - LIBRARY SIGNALS (apps/library/signals.py)
Nega bu fayl kerak: Foydalanuvchi yaratilganda uning o'qish statistikasi
jadvalini avtomatik yaratib qo'yish.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserReadingStatistic

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_reading_statistic(sender, instance, created: bool, **kwargs):
    """Yangi kitobxon ochilsa, statistika jadvalini avtomat ulab qo'yish."""
    if created:
        UserReadingStatistic.objects.get_or_create(user=instance)
        logger.info(f"{instance.username} uchun o'qish statistikasi jadvali yaratildi.")
