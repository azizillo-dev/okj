"""
OKJ PLATFORM - AUTHENTICATION SELECTORS (apps/authentication/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha seanslar va OTP larni
o'qish so'rovlari faqat shu yerda yoziladi.
"""

from typing import Optional
from django.db.models import QuerySet
from shared.selectors import BaseSelector
from .models import OTPCode, UserDevice, LoginHistory


class AuthSelector(BaseSelector):
    """Xavfsizlik va avtorizatsiya ma'lumotlarini o'qish selektorlari."""

    @classmethod
    def get_valid_otp(cls, phone_number: str, code: str) -> Optional[OTPCode]:
        """Telefon va kod bo'yicha ishlatilmagan va muddati o'tmagan OTP ni topish."""
        return OTPCode.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False,
        ).order_by("-created_at").first()

    @classmethod
    def get_user_devices(cls, user_id) -> QuerySet[UserDevice]:
        """Foydalanuvchining barcha faol seanslari / qurilmalari ro'yxati."""
        return UserDevice.objects.filter(user_id=user_id, is_active=True).order_by("-last_active_at")

    @classmethod
    def get_device_by_id(cls, user_id, device_id: str) -> Optional[UserDevice]:
        """Aniq bitta qurilma / seansni olish."""
        return UserDevice.objects.filter(user_id=user_id, device_id=device_id, is_active=True).first()

    @classmethod
    def get_login_history(cls, user_id, limit: int = 50) -> QuerySet[LoginHistory]:
        """Kitobxonning oxirgi kirish urinishlari auditi."""
        return LoginHistory.objects.filter(user_id=user_id).order_by("-created_at")[:limit]
