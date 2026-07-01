"""
OKJ PLATFORM - AUTHENTICATION SIGNALS (apps/authentication/signals.py)
Nega bu fayl kerak: Shubhali kirishlar yuz berganda adminlarga yoki
loglarga ogohlantirish yuborish.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LoginHistory

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LoginHistory)
def log_failed_login_attempts(sender, instance: LoginHistory, created: bool, **kwargs):
    """Muvaffaqiyatsiz kirish urinishini qayd etish."""
    if created and instance.status == LoginHistory.Status.FAILED:
        logger.warning(f"Xavfsizlik ogohlantirishi: {instance.phone_number} dan xato kirish urinishi ({instance.ip_address})")
