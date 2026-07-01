"""
OKJ PLATFORM - FOLLOWS SELECTORS (apps/follows/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari va N+1 muammosiz obunachilar ro'yxatini yuklash shu yerda bajariladi.
"""

from django.db.models import QuerySet
from shared.selectors import BaseSelector
from .models import Follow


class FollowSelector(BaseSelector):
    """Kitobxon obunachilari va ergashganlarini N+1 muammosiz yuklash selektori."""

    @classmethod
    def get_followers(cls, user_id) -> QuerySet[Follow]:
        """Foydalanuvchining barcha aktiv obunachilari (Followers)."""
        return (
            Follow.objects.select_related("follower")
            .filter(following_id=user_id, is_deleted=False)
            .order_by("-created_at")
        )

    @classmethod
    def get_following(cls, user_id) -> QuerySet[Follow]:
        """Foydalanuvchi kimlarga ergashgan (Following)."""
        return (
            Follow.objects.select_related("following")
            .filter(follower_id=user_id, is_deleted=False)
            .order_by("-created_at")
        )

    @classmethod
    def is_following(cls, follower, target_user_id) -> bool:
        """Kitobxon ushbu foydalanuvchini kuzatyaptimi yoki yo'qmi."""
        if not follower or not follower.is_authenticated:
            return False
        return Follow.objects.filter(follower=follower, following_id=target_user_id, is_deleted=False).exists()

    @classmethod
    def get_followers_count(cls, user_id) -> int:
        """Tezkor obunachilar soni."""
        return Follow.objects.filter(following_id=user_id, is_deleted=False).count()

    @classmethod
    def get_following_count(cls, user_id) -> int:
        """Tezkor ergashilganlar soni."""
        return Follow.objects.filter(follower_id=user_id, is_deleted=False).count()
