"""
OKJ PLATFORM - INTERACTIONS MODELS (apps/interactions/models.py)
Nega bu fayl kerak: Kitobxonlarning postlarga bosgan layklari va
saqlab qo'ygan (bookmark) postlarini xavfsiz, takrorlanmas va tezkor saqlash.
"""

from django.db import models
from django.db.models import Q
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from posts.models import Post


class PostLike(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Postga bosilgan Layk modeli.
    Constraints: Bitta user bitta postga faqat 1 marta aktiv layk bosishi mumkin.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        verbose_name = "Post Layki"
        verbose_name_plural = "Post Layklari"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                condition=Q(is_deleted=False),
                name="unique_active_post_like",
            )
        ]
        indexes = [
            models.Index(fields=["user", "post", "is_deleted"], name="idx_like_user_post"),
            models.Index(fields=["post", "-created_at"], name="idx_like_post_time"),
        ]

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.id}"


class PostBookmark(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Saqlangan post (Bookmark / Collection) modeli.
    Constraints: Bitta user bitta postni faqat 1 marta aktiv saqlashi mumkin.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_bookmarks"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    collection_name = models.CharField(
        max_length=100, default="Asosiy", help_text="Instagram to'plamlar (papka) nomi"
    )

    class Meta:
        verbose_name = "Saqlangan Post (Bookmark)"
        verbose_name_plural = "Saqlangan Postlar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                condition=Q(is_deleted=False),
                name="unique_active_post_bookmark",
            )
        ]
        indexes = [
            models.Index(fields=["user", "post", "is_deleted"], name="idx_bm_user_post"),
            models.Index(fields=["user", "-created_at"], name="idx_bm_user_time"),
        ]

    def __str__(self):
        return f"{self.user.username} 🔖 {self.post.id} ({self.collection_name})"
