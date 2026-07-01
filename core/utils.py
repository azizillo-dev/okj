"""
OKJ PLATFORM - GENERAL UTILITIES (core/utils.py)
Nega bu fayl kerak: Loyihaning turli joylarida ishlatiladigan IP aniqlash, 
noyob pasport raqami (OKJ-XXXXX) generatsiya qilish kabi yordamchi funksiyalar.
"""

import random
import string


def get_client_ip(request) -> str:
    """Foydalanuvchining haqiqiy IP manzilini Nginx x-forwarded-for orqali aniqlash."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def generate_random_numeric_code(length: int = 4) -> str:
    """SMS tasdiqlash uchun tasodifiy raqamli kod (m-n: '8492')."""
    return "".join(random.choices(string.digits, k=length))


def generate_okj_id(number: int) -> str:
    """Int raqamni chiroyli OKJ pasport raqamiga aylantirish (m-n: 10492 -> 'OKJ-10492')."""
    return f"OKJ-{number:05d}"
