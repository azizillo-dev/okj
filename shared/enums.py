"""
OKJ PLATFORM - SHARED PYTHON ENUMS (shared/enums.py)
Nega bu fayl kerak: Python'ning sof Enum klasslari ma'lumotlar bazasiga yozilmaydigan,
lekin biznes logikada (services.py) ishlatiladigan xabarlar va hodisalarni boshqarish uchun.
"""

from enum import Enum


class NotificationChannel(str, Enum):
    PUSH = "PUSH"
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"


class GamificationEvent(str, Enum):
    DAILY_CHECKIN = "DAILY_CHECKIN"
    NEW_POST = "NEW_POST"
    BOOK_REVIEW = "BOOK_REVIEW"
    EXCHANGE_COMPLETED = "EXCHANGE_COMPLETED"
