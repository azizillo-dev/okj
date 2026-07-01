"""
OKJ PLATFORM - INTERACTIONS SELECTORS (apps/interactions/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari va N+1 muammosiz optimizatsiyalar shu yerda bajariladi.
"""

from typing import Optional
from django.db.models import QuerySet
from shared.selectors import BaseSelector
from .models import PostLike, PostBookmark
from posts.models import Post


class InteractionSelector(BaseSelector):
    """Post layklari va saqlanganlarni o'qish selektori."""

    @classmethod
    def get_post_likes(cls, post: Post) -> QuerySet[PostLike]:
        """Postga bosilgan barcha aktiv layk yozuvlari."""
        return PostLike.objects.select_related("user").filter(post=post, is_deleted=False).order_by("-created_at")

    @classmethod
    def get_user_liked_posts(cls, user) -> QuerySet[PostLike]:
        """Kitobxon layk bosgan postlar ro'yxati (Post va muallifi o'ralgan)."""
        return (
            PostLike.objects.select_related("post", "post__user", "post__book")
            .prefetch_related("post__media")
            .filter(user=user, is_deleted=False)
            .order_by("-created_at")
        )

    @classmethod
    def get_user_bookmarked_posts(cls, user, collection_name: Optional[str] = None) -> QuerySet[PostBookmark]:
        """Kitobxon saqlab qo'ygan postlar ro'yxati."""
        qs = (
            PostBookmark.objects.select_related("post", "post__user", "post__book")
            .prefetch_related("post__media")
            .filter(user=user, is_deleted=False)
        )
        if collection_name:
            qs = qs.filter(collection_name=collection_name)
        return qs.order_by("-created_at")

    @classmethod
    def is_post_liked_by_user(cls, post: Post, user) -> bool:
        """Kitobxon ushbu postga layk bosganmi yoki yo'q."""
        if not user or not user.is_authenticated:
            return False
        return PostLike.objects.filter(post=post, user=user, is_deleted=False).exists()

    @classmethod
    def is_post_bookmarked_by_user(cls, post: Post, user) -> bool:
        """Kitobxon ushbu postni saqlab qo'yganmi yoki yo'q."""
        if not user or not user.is_authenticated:
            return False
        return PostBookmark.objects.filter(post=post, user=user, is_deleted=False).exists()
