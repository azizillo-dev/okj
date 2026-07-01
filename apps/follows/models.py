"""
OKJ PLATFORM - FOLLOWS MODELS (apps/follows/models.py)
Nega bu fayl kerak: Kitobxonlarning bir-biriga obuna bo'lishi (Ijtimoiy graf),
self-follow taqiqi va takrorlanmas obunalarni nazorat qilish.
"""

from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel


class Follow(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Kitobxon obunasi (Follow) modeli.
    Constraints:
      1. Bitta kitobxon faqat 1 marta aktiv obuna bo'la oladi.
      2. Kitobxon o'z-o'ziga obuna bo'lishi taqiqlangan (Self-Follow constraint).
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following_relationships"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follower_relationships"
    )

    class Meta:
        verbose_name = "Obuna"
        verbose_name_plural = "Obunalar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                condition=Q(is_deleted=False),
                name="unique_active_follow",
            ),
            models.CheckConstraint(
                check=~Q(follower=F("following")),
                name="prevent_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "following", "is_deleted"], name="idx_flw_pair"),
            models.Index(fields=["following", "is_deleted"], name="idx_flw_target"),
            models.Index(fields=["follower", "-created_at"], name="idx_flw_er_time"),
        ]

    def clean(self):
        super().clean()
        if self.follower_id == self.following_id:
            raise ValidationError("O'z-o'zingizga obuna bo'lishingiz mumkin emas.")

    def __str__(self):
        return f"{self.follower.username} ➡️ {self.following.username}"
