"""
OKJ PLATFORM - LIBRARY VALIDATORS (apps/library/validators.py)
Nega bu fayl kerak: O'qilgan sahifalar, foydalanuvchi baholari va maqsadlar
validatsiyasini nazorat qilish.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_user_rating(value: int) -> None:
    """Baho faqat 1 va 5 orasida bo'lishi kerak."""
    if value is not None and (value < 1 or value > 5):
        raise ValidationError("Baho 1 va 5 oralig'ida bo'lishi shart.")


def validate_positive_pages(value: int) -> None:
    """Sahifalar soni manfiy bo'lmasligi kerak."""
    if value is not None and value < 0:
        raise ValidationError("Sahifalar soni 0 yoki undan katta bo'lishi kerak.")


def validate_challenge_year(value: int) -> None:
    """Challengelar yili 2024 dan kelasi yilgacha bo'lishi mumkin."""
    current_year = timezone.now().year
    if value < 2024 or value > current_year + 1:
        raise ValidationError(f"Maqsad yili 2024 va {current_year + 1} oralig'ida bo'lishi shart.")


def validate_challenge_month(value: int) -> None:
    """Oylik challenge uchun oy 1-12 oralig'ida bo'lishi shart."""
    if value is not None and (value < 1 or value > 12):
        raise ValidationError("Oy 1 va 12 oralig'ida bo'lishi shart.")
