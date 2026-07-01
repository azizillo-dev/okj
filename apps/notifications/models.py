"""
OKJ PLATFORM - NOTIFICATIONS MODELS (apps/notifications/models.py)
Nega bu fayl kerak: Barcha modullardagi interaksiya hodisalarini
(Layk, Izoh, Obuna, Yutuq) markazlashgan va asinxron saqlash.
"""

from django.db import models
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel


class NotificationType(models.TextChoices):
    LIKE = "LIKE", "Layk bosildi"
    COMMENT = "COMMENT", "Izoh qoldirildi"
    FOLLOW = "FOLLOW", "Yangi obunachi"
    READING_GOAL = "READING_GOAL", "O'qish chaqirig'i yutuqlari"
    SYSTEM = "SYSTEM", "Tizim xabari"


class Notification(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Markazlashgan Bildirishnoma modeli.
    Kitobxonning kirish qutisidagi (Inbox) barcha xabarlar shu yerda saqlanadi.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
        help_text="Hodisani amalga oshirgan shaxs (tizim xabarida null)",
    )
    notification_type = models.CharField(
        max_length=50, choices=NotificationType.choices, default=NotificationType.SYSTEM
    )
    target_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Tegishli resurs IDsi, masalan post_id yoki comment_id",
    )
    text = models.TextField(help_text="Bildirishnoma matni")
    is_read = models.BooleanField(default=False, help_text="O'qilganlik holati")
    read_at = models.DateTimeField(null=True, blank=True, help_text="O'qilgan vaqt")

    class Meta:
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["recipient", "is_read", "is_deleted", "-created_at"],
                name="idx_notif_inbox",
            ),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else "Tizim"
        return f"To {self.recipient.username} [{self.notification_type}]: {self.text[:30]}"
