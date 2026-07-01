"""
OKJ PLATFORM - FOLLOWS SERVICES (apps/follows/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari,
O(1) tezlikdagi Row-Reuse / Toggle va Self-Follow taqiqi @transaction.atomic ostida.
"""

from typing import Tuple
from django.db import transaction
from django.utils import timezone
from core.exceptions import ApplicationError
from shared.services import BaseService
from .models import Follow
from accounts.models import User


class FollowService(BaseService):
    """Kitobxonlarning obuna bo'lishi va bekor qilishini boshqaruvchi servis."""

    @classmethod
    @transaction.atomic
    def follow_user(cls, follower, following_id) -> Follow:
        """
        Boshqa kitobxonga obuna bo'lish.
        Agar avval obuna bo'lib o'chirilgan bo'lsa, O(1) tezlikda eski satr qayta tiklanadi.
        """
        if str(follower.id) == str(following_id):
            raise ApplicationError("O'z-o'zingizga obuna bo'lishingiz mumkin emas.", code="SELF_FOLLOW_DENIED")

        target_user = User.objects.filter(id=following_id, is_active=True).first()
        if not target_user:
            raise ApplicationError("Kuzatilayotgan foydalanuvchi topilmadi.", code="USER_NOT_FOUND")

        follow_obj = Follow.all_objects.filter(follower=follower, following=target_user).first()
        if follow_obj:
            if follow_obj.is_deleted:
                follow_obj.is_deleted = False
                follow_obj.deleted_at = None
                follow_obj.save(update_fields=["is_deleted", "deleted_at"])
                cls._on_user_followed(follower, target_user)
            return follow_obj

        follow_obj = Follow.objects.create(follower=follower, following=target_user)
        cls._on_user_followed(follower, target_user)
        return follow_obj

    @classmethod
    @transaction.atomic
    def unfollow_user(cls, follower, following_id) -> None:
        """Obunani bekor qilish (Soft Delete)."""
        follow_obj = Follow.objects.filter(follower=follower, following_id=following_id, is_deleted=False).first()
        if follow_obj:
            follow_obj.is_deleted = True
            follow_obj.deleted_at = timezone.now()
            follow_obj.save(update_fields=["is_deleted", "deleted_at"])

    @classmethod
    @transaction.atomic
    def toggle_follow(cls, follower, following_id) -> Tuple[Follow, bool]:
        """
        Obuna holatini tezkor almashtirish (Toggle).
        Qaytadi: (Follow yoki None, created_or_restored: bool)
        """
        active_follow = Follow.objects.filter(follower=follower, following_id=following_id, is_deleted=False).first()
        if active_follow:
            cls.unfollow_user(follower=follower, following_id=following_id)
            return active_follow, False

        new_follow = cls.follow_user(follower=follower, following_id=following_id)
        return new_follow, True

    @classmethod
    def _on_user_followed(cls, follower, following):
        """
        Kelajakda Notification moduli va Feed Ranking tizimlarini
        ulash uchun asinxron zamin (Helper Method).
        """
        # Obuna bo'linganda kitobxonga 5 XP berish (ijtimoiy faollik uchun)
        from accounts.services import UserService
        UserService.add_xp(user=follower, amount=5, reason="Yangi kitobxonni kuzata boshladingiz")
