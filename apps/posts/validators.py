"""
OKJ PLATFORM - POSTS VALIDATORS (apps/posts/validators.py)
Nega bu fayl kerak: Postlarga qo'yiladigan taqriz baholari,
rasmlar buyurtmasi va 30 daqiqalik media tahrir cheklovlarini nazorat qilish.
"""

from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.exceptions import ApplicationError


def validate_review_rating(value: int) -> None:
    """Taqriz postlarda baho 1 va 5 oralig'ida bo'lishi shart."""
    if value is not None and (value < 1 or value > 5):
        raise ValidationError("Taqriz bahosi 1 va 5 oralig'ida bo'lishi shart.")


def validate_media_order(value: int) -> None:
    """Rasm tartibi (order) 0 yoki undan katta bo'lishi kerak."""
    if value is not None and value < 0:
        raise ValidationError("Rasm tartibi raqami 0 yoki undan katta bo'lishi kerak.")


def check_media_edit_timeframe(published_at) -> None:
    """
    Chop etilganidan keyin 30 daqiqadan so'ng post rasmlarini
    tahrirlash yoki yangilash taqiqlanadi.
    """
    if not published_at:
        return
    thirty_mins_ago = timezone.now() - timedelta(minutes=30)
    if published_at < thirty_mins_ago:
        raise ApplicationError(
            "Xavfsizlik qoidasi: Chop etilganiga 30 daqiqadan oshgan post rasmlarini o'zgartirib bo'lmaydi.",
            code="MEDIA_EDIT_EXPIRED",
            status_code=403,
        )
