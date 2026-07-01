"""
OKJ PLATFORM - COMMENTS MODELS (apps/comments/models.py)
Nega bu fayl kerak: Postlar ostidagi muhokamalar va maksimal 2-darajali
(Flat-Tree) ierarxiyadagi izohlarni saqlash.
"""

from django.db import models
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from posts.models import Post
from .validators import validate_comment_text


class Comment(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Post Izohi (Comment) modeli.
    Ota-bola (Parent-Reply) bog'lanishi orqali izohlarga javob yozish mumkin.
    Flat-Tree qoidasi bo'yicha maksimal chuqurlik 2 daraja.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Ota izoh (Agar null bo'lsa - Root Comment / Asosiy izoh)",
    )
    text = models.TextField(
        max_length=1000,
        validators=[validate_comment_text],
        help_text="Izoh matni (maksimal 1000 belgi)",
    )
    is_approved = models.BooleanField(default=True, help_text="Moderatsiyadan o'tganligi")

    class Meta:
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["post", "parent", "is_deleted", "is_approved"],
                name="idx_comment_post_tree",
            ),
            models.Index(fields=["user", "-created_at"], name="idx_comment_user_time"),
        ]

    def __str__(self):
        parent_info = f" (Reply to {self.parent_id})" if self.parent_id else " (Root)"
        return f"{self.user.username}: {self.text[:30]}...{parent_info}"
