"""
OKJ PLATFORM - VALIDATORS (core/validators.py)
Nega bu fayl kerak: O'zbekiston telefon raqamlari formatini (+998XXXXXXXXX)
va pasport raqamlari formatini aniq tekshirish uchun.
"""

import re
from django.core.exceptions import ValidationError


def validate_uzbek_phone_number(value: str) -> None:
    """Telefon raqami +998 bilan boshlanishi va to'g'ri uzunlikda ekanligini tekshiradi."""
    pattern = r"^\+998[0-9]{9}$"
    if not re.match(pattern, value):
        raise ValidationError("Telefon raqami +998XXXXXXXXX formatida bo'lishi shart.")


def validate_okj_id_format(value: str) -> None:
    """OKJ pasport raqami OKJ-XXXXX formatida bo'lishi shart."""
    pattern = r"^OKJ-\d{5,}$"
    if not re.match(pattern, value):
        raise ValidationError("Pasport raqami OKJ-XXXXX (m-n: OKJ-10492) formatida bo'lishi kerak.")
