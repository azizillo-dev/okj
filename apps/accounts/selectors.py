"""
OKJ PLATFORM - ACCOUNTS SELECTORS (apps/accounts/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari faqat shu yerda yoziladi. Bu N+1 so'rov xatolaridan va viewlar ichida
xato ORM filterlar yozilishidan saqlaydi.
"""

from typing import Optional
from django.db.models import QuerySet
from shared.selectors import BaseSelector
from .models import User, District


class UserSelector(BaseSelector):
    """Kitobxon ma'lumotlarini o'qish selektori."""

    @classmethod
    def get_user_by_id(cls, user_id) -> Optional[User]:
        """Foydalanuvchini ID si bo'yicha (district bilan birga JOIN qilib) olish."""
        return User.objects.select_related("district").filter(id=user_id).first()

    @classmethod
    def get_user_by_okj_id(cls, okj_id: str) -> Optional[User]:
        """Foydalanuvchini OKJ-ID si bo'yicha olish."""
        return User.objects.select_related("district").filter(okj_id=okj_id).first()

    @classmethod
    def get_user_by_phone(cls, phone_number: str) -> Optional[User]:
        """Telefon raqami bo'yicha qidirish."""
        return User.objects.select_related("district").filter(phone_number=phone_number).first()

    @classmethod
    def get_district_leaderboard(cls, district_id: int, limit: int = 50) -> QuerySet[User]:
        """Tuman bo'yicha eng yuqori XP ga ega kitobxonlar reytingi."""
        return User.objects.filter(district_id=district_id).order_by("-total_xp")[:limit]


class DistrictSelector(BaseSelector):
    """Viloyat va Tumanlar ro'yxatini o'qish selektori."""

    @classmethod
    def get_all_districts(cls) -> QuerySet[District]:
        """Barcha tumanlarni viloyat nomi bo'yicha saralab berish."""
        return District.objects.all().order_by("region_name", "name")

    @classmethod
    def get_districts_by_region(cls, region_name: str) -> QuerySet[District]:
        """Viloyat nomi bo'yicha tegishli tumanlarni olish."""
        return District.objects.filter(region_name=region_name).order_by("name")
