"""
OKJ PLATFORM - ACCOUNTS MANAGERS (apps/accounts/managers.py)
Nega bu fayl kerak: Custom User modelimizda `username` emas, balki telefon raqami yoki
Google ID orqali hamda Soft Delete hisobga olinib foydalanuvchi yaratuvchi menedjer.
"""

from django.contrib.auth.models import BaseUserManager
from django.db import models


class ActiveUserManager(BaseUserManager):
    """Faqat o'chirilmagan (is_deleted=False) va faol foydalanuvchilar bilan ishlovchi menedjer."""
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)

    def create_user(self, phone_number=None, password=None, **extra_fields):
        """Oddiy foydalanuvchi yaratish."""
        if not phone_number and not extra_fields.get("google_id") and not extra_fields.get("username"):
            raise ValueError("Foydalanuvchi yaratish uchun telefon raqami yoki Google ID bo'lishi shart.")

        if not extra_fields.get("username"):
            # Agar username berilmasa, telefon yoki google_id dan vaqtinchalik username yasaymiz
            extra_fields["username"] = phone_number or f"google_{extra_fields.get('google_id')}"

        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def createsuperuser(self, username, password=None, **extra_fields):
        """Superuser (Admin) yaratish."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is_staff=True bo'lishi shart.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser=True bo'lishi shart.")

        return self.create_user(phone_number=username, password=password, username=username, **extra_fields)
