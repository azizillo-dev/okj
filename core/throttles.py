"""
OKJ PLATFORM - CUSTOM THROTTLE CLASSES (core/throttles.py)
Nega bu fayl kerak: OTP so'rash endpointi uchun alohida qattiq rate limiting.
SIM-swapping va SMS spam hujumlaridan himoya: bir IP'dan soatiga 5 ta so'rovdan ko'p ruxsat yo'q.
"""

from rest_framework.throttling import AnonRateThrottle


class OtpRequestThrottle(AnonRateThrottle):
    """
    SMS OTP so'rash uchun maxsus throttling.
    base.py'dagi DEFAULT_THROTTLE_RATES['otp_request'] = '5/hour' sozlamasidan foydalanadi.

    Nega AnonRateThrottle: OTP so'rashda foydalanuvchi hali autentifikatsiya qilinmagan,
    shuning uchun IP manzil asosida limitlash qo'llaniladi.
    """
    scope = "otp_request"
