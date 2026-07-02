"""
OKJ PLATFORM - MODERATION MODELS (apps/moderation/models.py)
Nega bu fayl kerak: Kontent nazorati, shikoyatlar (reports) va kitobxonlar
moderatsiya holatini (shadow ban) markazlashtirilgan tarzda saqlash.
"""

from django.db import models
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel


class ContentReport(UUIDModel, TimeStampedModel):
    """
    POST, COMMENT va BOOK uchun YAGONA va markazlashgan shikoyat modeli.
    """
    class ReportReason(models.TextChoices):
        SPAM = "SPAM", "Spam yoki reklama"
        HARASSMENT = "HARASSMENT", "Haqorat yoki shilqimlik"
        COPYRIGHT = "COPYRIGHT", "Mualliflik huquqini buzish"
        INAPPROPRIATE = "INAPPROPRIATE", "Nomos kontent"

    class ReportStatus(models.TextChoices):
        PENDING = "PENDING", "Tekshirilmoqda"
        RESOLVED = "RESOLVED", "Hal qilingan"
        DISMISSED = "DISMISSED", "Rad etilgan"

    class ContentType(models.TextChoices):
        POST = "POST", "Post"
        COMMENT = "COMMENT", "Izoh"
        BOOK = "BOOK", "Kitob"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="content_reports"
    )
    content_type = models.CharField(max_length=20, choices=ContentType.choices, db_index=True)
    target_id = models.UUIDField(help_text="Shikoyat qilinayotgan kontent IDsi", db_index=True)
    reason = models.CharField(max_length=50, choices=ReportReason.choices, db_index=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING, db_index=True
    )
    moderator_notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Kontent Shikoyati"
        verbose_name_plural = "Kontent Shikoyatlari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "status", "-created_at"], name="idx_mod_queue_tree"),
        ]

    def __str__(self):
        return f"{self.reporter.username} -> {self.content_type} ({self.status})"


class UserModerationFlag(TimeStampedModel):
    """
    Kitobxonlarga shadow ban yoki boshqa moderatsiya cheklovlarini
    User modeliga tegmasdan 1-to-1 saqlovchi jadval.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moderation_flag", primary_key=True
    )
    is_shadow_banned = models.BooleanField(default=False, db_index=True)
    shadow_banned_at = models.DateTimeField(null=True, blank=True)
    shadow_banned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "Kitobxon Moderatsiya Flagi"
        verbose_name_plural = "Kitobxon Moderatsiya Flaglari"

    def __str__(self):
        return f"{self.user.username} (Shadow ban: {self.is_shadow_banned})"


class AdminActionLog(UUIDModel, TimeStampedModel):
    """
    Admin va moderatorlarning operatsion harakatlarini qayd etuvchi audit log jadvali.
    """
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_actions_performed"
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_actions_received"
    )
    action_type = models.CharField(max_length=50, db_index=True, help_text="m-n: BAN, UNBAN, GRANT_XP, RESOLVE_REPORT")
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Admin Harakati Logi"
        verbose_name_plural = "Admin Harakatlari Loglari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor.username} -> {self.action_type} ({self.created_at})"
