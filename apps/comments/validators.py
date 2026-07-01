"""
OKJ PLATFORM - COMMENTS VALIDATORS (apps/comments/validators.py)
Nega bu fayl kerak: Izoh matni bo'sh bo'lmasligi va maksimal 1000
belgidan oshmasligini nazorat qilish.
"""

from django.core.exceptions import ValidationError


def validate_comment_text(value: str):
    if not value or not value.strip():
        raise ValidationError("Izoh matni bo'sh bo'lishi mumkin emas.")
    if len(value.strip()) > 1000:
        raise ValidationError("Izoh matni 1000 belgidan oshmasligi shart.")
