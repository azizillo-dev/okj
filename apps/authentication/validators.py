"""
OKJ PLATFORM - AUTHENTICATION VALIDATORS (apps/authentication/validators.py)
Nega bu fayl kerak: Brute Force (parol va OTP kodni cheksiz taxmin qilib buzish)
hujumlarini nazorat qilish hamda telefon raqam formatlarini tekshirish.
"""

import re
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.exceptions import ApplicationError


def validate_auth_phone_number(value: str) -> None:
    """Telefon raqami +998XXXXXXXXX formatida ekanligini nazorat qiladi."""
    if not value or not re.match(r"^\+998[0-9]{9}$", value):
        raise ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi shart.")


def validate_otp_code_format(value: str) -> None:
    """OTP kod faqat 4 yoki 6 ta raqamdan iborat bo'lishi kerak."""
    if not value or not re.match(r"^\d{4,6}$", value):
        raise ValidationError("TASDIQLASH kodi (OTP) faqat 4-6 ta raqamdan iborat bo'lishi kerak.")


def check_brute_force_lockout(phone_number: str, ip_address: str = "") -> None:
    """
    So'nggi 15 daqiqada 5 martadan ortiq xato urinish bo'lgan bo'lsa,
    hisobni vaqtinchalik bloklash (Brute Force Protection).
    """
    from .models import LoginHistory
    fifteen_mins_ago = timezone.now() - timedelta(minutes=15)

    failed_attempts = LoginHistory.objects.filter(
        phone_number=phone_number,
        status="FAILED",
        created_at__gte=fifteen_mins_ago,
    ).count()

    if failed_attempts >= 5:
        raise ApplicationError(
            "Xavfsizlik tizimi: Ko'p sonli xato urinishlar aniqlandi. Iltimos 15 daqiqadan keyin qayta urinib ko'ring.",
            code="BRUTE_FORCE_LOCKOUT",
            status_code=429,
        )
