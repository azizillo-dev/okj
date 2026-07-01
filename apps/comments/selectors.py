"""
OKJ PLATFORM - COMMENTS SELECTORS (apps/comments/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari va N+1 muammosiz daraxtsimon yuklash shu yerda bajariladi.
"""

from typing import Optional
from django.db.models import QuerySet, Prefetch
from shared.selectors import BaseSelector
from .models import Comment


class CommentSelector(BaseSelector):
    """Post izohlarini N+1 muammosiz va 2-darajali daraxt ko'rinishida yuklash selektori."""

    @classmethod
    def get_comments_for_post(cls, post_id) -> QuerySet[Comment]:
        """
        Postga tegishli barcha asosiy (Root) izohlarni va ularning
        javoblarini (Replies) ko'pi bilan 2 ta SQL query orqali yuklaydi.
        """
        replies_prefetch = Prefetch(
            "replies",
            queryset=Comment.objects.select_related("user")
            .filter(is_approved=True)
            .order_by("created_at"),
        )

        return (
            Comment.objects.select_related("user")
            .prefetch_related(replies_prefetch)
            .filter(post_id=post_id, parent__isnull=True, is_approved=True)
            .order_by("created_at")
        )

    @classmethod
    def get_comment_by_id(cls, comment_id) -> Optional[Comment]:
        """Izohni ID bo'yicha (user va post bilan) yuklash."""
        return Comment.objects.select_related("user", "post", "parent").filter(id=comment_id).first()
