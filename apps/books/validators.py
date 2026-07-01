"""
OKJ PLATFORM - BOOKS VALIDATORS (apps/books/validators.py)
Nega bu fayl kerak: ISBN raqamlari standartlarga mosligini, nashr yillari reallikka
to'g'ri kelishini va muqova rasmlari xavfsizligini ta'minlash uchun.
"""

import re
import datetime
from django.core.exceptions import ValidationError
from core.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_UPLOAD_SIZE_MB


def validate_isbn_10(value: str) -> None:
    """ISBN-10 formati (10 ta raqam yoki oxiri X bilan tugaydigan) ekanligini tekshiradi."""
    if not value:
        return
    cleaned = value.replace("-", "").replace(" ", "").upper()
    if not re.match(r"^\d{9}[\dX]$", cleaned):
        raise ValidationError("ISBN-10 formati noto'g'ri. 10 ta raqam yoki 9 ta raqam va 'X' dan iborat bo'lishi kerak.")


def validate_isbn_13(value: str) -> None:
    """ISBN-13 formati (978 yoki 979 bilan boshlanuvchi 13 ta raqam) ekanligini tekshiradi."""
    if not value:
        return
    cleaned = value.replace("-", "").replace(" ", "")
    if not re.match(r"^(978|979)\d{10}$", cleaned):
        raise ValidationError("ISBN-13 formati noto'g'ri. 978 yoki 979 bilan boshlanib, 13 ta raqamdan iborat bo'lishi kerak.")


def validate_publication_year(value: int) -> None:
    """Kitob nashr yili 1000-yildan kelasi 2 yilgacha bo'lgan oraliqda ekanligini nazorat qiladi."""
    if not value:
        return
    current_year = datetime.date.today().year + 2
    if value < 1000 or value > current_year:
        raise ValidationError(f"Nashr yili 1000 va {current_year} yillar oralig'ida bo'lishi shart.")


def validate_cover_image_url_or_extension(url: str) -> None:
    """Muqova rasmining URL manzili yoki fayl kengaytmasi xavfsiz rasm ekanligini tekshiradi."""
    if not url:
        return
    ext = url.split(".")[-1].lower().split("?")[0]
    if ext not in ALLOWED_IMAGE_EXTENSIONS and not url.startswith("http"):
        raise ValidationError(f"Rasm formati noto'g'ri. Ruxsat etilganlar: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
