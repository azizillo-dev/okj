"""
OKJ PLATFORM - AUTHENTICATION MODELS (apps/authentication/models.py)
Nega bu fayl kerak: Barcha SMS OTP kodlar, faol seanslar (sessiyalar),
ishonchli qurilmalar va xavfsizlik audit loglarini bazada saqlash.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import UUIDModel, TimeStampedModel
from .validators import validate_auth_phone_number


class OTPCode(UUIDModel, TimeStampedModel):
    """
    Telefon raqamiga yuboriladigan bir martalik tasdiqlash kodi (OTP).
    Nega kerak: Parolsiz kirish (Passwordless auth) yoki 2FA tasdiqlash uchun.
    """
    class Purpose(models.TextChoices):
        LOGIN = "LOGIN", "Tizimga kirish"
        REGISTER = "REGISTER", "Ro'yxatdan o'tish"
        PASSWORDLESS = "PASSWORDLESS", "Parolsiz kirish"

    phone_number = models.CharField(max_length=20, validators=[validate_auth_phone_number], db_index=True)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.LOGIN)
    expires_at = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False)
    attempts_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "OTP Kodi"
        verbose_name_plural = "OTP Kodlari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number", "code", "is_used"]),
        ]

    def __str__(self):
        return f"{self.phone_number} ({self.code}) — {'Ishlatilgan' if self.is_used else 'Faol'}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at


class UserDevice(UUIDModel, TimeStampedModel):
    """
    Kitobxon foydalanadigan smartfon yoki brauzer (Session & Device Management).
    Nega kerak: "Barcha qurilmalardan chiqish" (Logout all devices) va ishonchli qurilmani belgilash.
    """
    class DeviceType(models.TextChoices):
        IOS = "IOS", "iOS (iPhone/iPad)"
        ANDROID = "ANDROID", "Android"
        WEB = "WEB", "Web Browser"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    device_id = models.CharField(max_length=255, db_index=True, help_text="Noyob qurilma identifikatori")
    device_type = models.CharField(max_length=20, choices=DeviceType.choices, default=DeviceType.WEB)
    device_name = models.CharField(max_length=255, blank=True, help_text="m-n: iPhone 15 Pro")
    fcm_token = models.CharField(max_length=500, blank=True, help_text="Push bildirishnoma tokeni")
    refresh_token_jti = models.CharField(max_length=255, blank=True, db_index=True, help_text="Joriy Refresh token ID")
    is_trusted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    last_active_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Qurilma / Seans"
        verbose_name_plural = "Qurilmalar va Seanslar"
        ordering = ["-last_active_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "device_id"], name="unique_user_device")
        ]

    def __str__(self):
        return f"{self.user.username} — {self.device_name or self.device_type}"


class LoginHistory(TimeStampedModel):
    """
    Tizimga kirish urinishlari auditi (Audit Log).
    Nega kerak: Hackerlar hujumlarini aniqlash va kitobxonga xavfsizlik tarixini ko'rsatish.
    """
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Muvaffaqiyatli"
        FAILED = "FAILED", "Xatolik / Muvaffaqiyatsiz"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="login_logs"
    )
    phone_number = models.CharField(max_length=20, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS, db_index=True)
    failure_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Kirish Tarixi (Audit)"
        verbose_name_plural = "Kirish Tarixalari (Audit)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone_number} — {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
