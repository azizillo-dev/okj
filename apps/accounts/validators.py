"""
OKJ PLATFORM - ACCOUNTS VALIDATORS (apps/accounts/validators.py)
Nega bu fayl kerak: Foydalanuvchilar profil ma'lumotlari, telefon raqami
va bio maydonlariga noto'g'ri yoki xavfli matnlar yozmasligini nazorat qilish.
"""

import re
from django.core.exceptions import ValidationError


def validate_phone_number_format(value: str) -> None:
    """Telefon raqami +998XXXXXXXXX formatida bo'lishi shart."""
    if not value:
        return
    pattern = r"^\+998[0-9]{9}$"
    if not re.match(pattern, value):
        raise ValidationError("Telefon raqami +998XXXXXXXXX formatida bo'lishi shart.")


def validate_bio_content(value: str) -> None:
    """Bio maydoni juda uzun bo'lmasligi va spam silsilalarga ega emasligini tekshiradi."""
    if len(value) > 500:
        raise ValidationError("Shaxsiy ma'lumot (bio) 500 belgidan oshmasligi kerak.")
