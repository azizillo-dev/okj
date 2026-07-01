"""
OKJ PLATFORM - POSTS SELECTORS (apps/posts/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari va N+1 muammosiz optimizatsiyalar shu yerda bajariladi.
"""

from typing import Optional
from django.db.models import QuerySet, Q
from shared.selectors import BaseSelector
from .models import Post, DraftPost


class PostSelector(BaseSelector):
    """Postlar tasmasi (feed), qidiruv va profildagi postlarni o'qish selektori."""

    @staticmethod
    def _base_queryset() -> QuerySet[Post]:
        """N+1 so'rovlardan xoli asosiy QuerySet."""
        return (
            Post.published_objects.select_related("user", "book", "district", "library_item")
            .prefetch_related("media")
        )

    @classmethod
    def get_feed_posts(
        cls,
        post_type: Optional[str] = None,
        district_id: Optional[int] = None,
        book_id: Optional[str] = None,
        hashtag: Optional[str] = None,
    ) -> QuerySet[Post]:
        """
        Asosiy ijtimoiy lenta (feed) uchun filtrlangan postlar.
        """
        qs = cls._base_queryset()

        if post_type:
            qs = qs.filter(post_type=post_type)
        if district_id:
            qs = qs.filter(district_id=district_id)
        if book_id:
            qs = qs.filter(book_id=book_id)
        if hashtag:
            clean_tag = hashtag if hashtag.startswith("#") else f"#{hashtag}"
            qs = qs.filter(hashtags__icontains=clean_tag)

        return qs

    @classmethod
    def get_post_by_slug(cls, slug: str) -> Optional[Post]:
        return Post.objects.select_related("user", "book", "district").prefetch_related("media").filter(slug=slug).first()

    @classmethod
    def get_post_by_id(cls, post_id) -> Optional[Post]:
        return Post.objects.select_related("user", "book", "district").prefetch_related("media").filter(id=post_id).first()

    @classmethod
    def get_user_posts(cls, user_id, status: Optional[str] = None) -> QuerySet[Post]:
        """Kitobxonning o'z profilidagi postlari ro'yxati."""
        qs = Post.objects.select_related("book", "district").prefetch_related("media").filter(user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @classmethod
    def get_user_drafts(cls, user_id) -> QuerySet[DraftPost]:
        """Kitobxonning qoralamalari."""
        return DraftPost.objects.select_related("book").filter(user_id=user_id).order_by("-updated_at")
