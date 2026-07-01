"""
OKJ PLATFORM - POSTS SIGNALS (apps/posts/signals.py)
Nega bu fayl kerak: Post yaratilganda uning 1-to-1 view hisoblagichini
avtomatik nazorat qilib turish.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, PostViewCounter

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def ensure_post_view_counter(sender, instance, created: bool, **kwargs):
    """Yangi post ochilsa, ko'rishlar hisoblagichi jadvalini avtomat ulab qo'yish."""
    if created:
        PostViewCounter.objects.get_or_create(post=instance)
