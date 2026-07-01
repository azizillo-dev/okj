"""
OKJ PLATFORM - ACCOUNTS SIGNALS (apps/accounts/signals.py)
Nega bu fayl kerak: Foydalanuvchilar o'chirilganda yoki yozilganda kashni tozalash
va log yozish kabi asinxron yoki fon hodisalarini kuzatish.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance: User, created: bool, **kwargs):
    """Yangi kitobxon ro'yxatdan o'tganda log qoldiramiz."""
    if created:
        logger.info(f"Yangi kitobxon tizimga qo'shildi: {instance.okj_id} ({instance.phone_number})")
