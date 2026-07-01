"""
OKJ PLATFORM - AUTHENTICATION SERVICES (apps/authentication/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari
va xavfsizlik mantiqlari (OTP tekshirish, token berish, seans yopish) faqat shu yerda
@transaction.atomic ostida bo'ladi.
"""

from datetime import timedelta
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from core.exceptions import ApplicationError
from core.utils import generate_random_numeric_code
from accounts.models import User
from accounts.services import UserService
from accounts.selectors import UserSelector
from shared.services import BaseService
from .models import OTPCode, UserDevice, LoginHistory
from .validators import check_brute_force_lockout
from .selectors import AuthSelector


class AuthService(BaseService):
    """Tizimga kirish, parolsiz tasdiqlash va seanslarni boshqarish servisi."""

    @classmethod
    @transaction.atomic
    def request_otp(cls, phone_number: str, purpose: str = OTPCode.Purpose.LOGIN) -> OTPCode:
        """
        Telefon raqamga 4 xonali tasdiqlash kodi yuborish.
        Nega tranzaksiya: Eski faol kodlarni o'chirib yangisini yozish atomik bo'lishi shart.
        """
        check_brute_force_lockout(phone_number=phone_number)

        # Eski faol kodlarni bekor qilamiz
        OTPCode.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)

        code = generate_random_numeric_code(length=4)
        expires_at = timezone.now() + timedelta(minutes=3)

        otp = OTPCode.objects.create(
            phone_number=phone_number,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
        )
        # Haqiqiy loyihada bu yerda Eskiz / PlayMobile SMS Gateway chaqiriladi
        return otp

    @classmethod
    @transaction.atomic
    def verify_otp_and_login(
        cls,
        phone_number: str,
        code: str,
        ip_address: str = "",
        user_agent: str = "",
        device_id: str = "default_web",
        device_type: str = UserDevice.DeviceType.WEB,
        device_name: str = "",
        fcm_token: str = "",
    ) -> Dict[str, Any]:
        """
        OTP kodni tasdiqlab, JWT tokenlar (Access + Refresh) berish va qurilmani qayd etish.
        """
        check_brute_force_lockout(phone_number=phone_number, ip_address=ip_address)

        otp = AuthSelector.get_valid_otp(phone_number=phone_number, code=code)
        if not otp or otp.is_expired:
            LoginHistory.objects.create(
                phone_number=phone_number,
                ip_address=ip_address,
                user_agent=user_agent,
                status=LoginHistory.Status.FAILED,
                failure_reason="Noto'g'ri yoki muddati o'tgan OTP kodi",
            )
            raise ApplicationError("Kiritilgan tasdiqlash kodi xato yoki uning muddati o'tgan.")

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        # Kitobxonni topamiz yoki avtomatik ro'yxatdan o'tkazamiz (Passwordless Auth)
        user = UserSelector.get_user_by_phone(phone_number)
        if not user:
            user = UserService.register_reader(phone_number=phone_number)

        return cls._issue_tokens_and_register_device(
            user=user,
            phone_number=phone_number,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            device_type=device_type,
            device_name=device_name,
            fcm_token=fcm_token,
        )

    @classmethod
    @transaction.atomic
    def login_with_password(
        cls,
        phone_number: str,
        password: str,
        ip_address: str = "",
        user_agent: str = "",
        device_id: str = "default_web",
        device_type: str = UserDevice.DeviceType.WEB,
        device_name: str = "",
        fcm_token: str = "",
    ) -> Dict[str, Any]:
        """Parol orqali an'anaviy kirish servisi."""
        check_brute_force_lockout(phone_number=phone_number, ip_address=ip_address)

        user = UserSelector.get_user_by_phone(phone_number)
        if not user or not user.check_password(password):
            LoginHistory.objects.create(
                phone_number=phone_number,
                ip_address=ip_address,
                user_agent=user_agent,
                status=LoginHistory.Status.FAILED,
                failure_reason="Noto'g'ri telefon raqami yoki parol",
            )
            raise ApplicationError("Telefon raqami yoki parol xato.")

        return cls._issue_tokens_and_register_device(
            user=user,
            phone_number=phone_number,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            device_type=device_type,
            device_name=device_name,
            fcm_token=fcm_token,
        )

    @classmethod
    @transaction.atomic
    def google_login_service(
        cls,
        google_id: str,
        email: str = "",
        full_name: str = "",
        ip_address: str = "",
        user_agent: str = "",
        device_id: str = "google_web",
        device_type: str = UserDevice.DeviceType.WEB,
        device_name: str = "",
    ) -> Dict[str, Any]:
        """Google OAuth tayyorgarlik servisi."""
        user = User.objects.filter(google_id=google_id).first()
        if not user:
            first_name = full_name.split(" ")[0] if full_name else "Kitobxon"
            last_name = " ".join(full_name.split(" ")[1:]) if len(full_name.split(" ")) > 1 else ""
            user = UserService.register_reader(phone_number="", first_name=first_name, last_name=last_name, google_id=google_id)

        return cls._issue_tokens_and_register_device(
            user=user,
            phone_number=user.phone_number or f"google:{google_id}",
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            device_type=device_type,
            device_name=device_name,
        )

    @classmethod
    def _issue_tokens_and_register_device(
        cls,
        user: User,
        phone_number: str,
        ip_address: str,
        user_agent: str,
        device_id: str,
        device_type: str,
        device_name: str,
        fcm_token: str = "",
    ) -> Dict[str, Any]:
        """JWT tokenlar berish, audit log yozish va seansni yangilash."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        jti = refresh.payload.get("jti", "")

        # Qurilmani qayd etish
        UserDevice.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                "device_type": device_type,
                "device_name": device_name or device_type,
                "fcm_token": fcm_token,
                "refresh_token_jti": jti,
                "is_active": True,
                "last_active_at": timezone.now(),
            },
        )

        # Audit log (SUCCESS)
        LoginHistory.objects.create(
            user=user,
            phone_number=phone_number,
            ip_address=ip_address,
            user_agent=user_agent,
            status=LoginHistory.Status.SUCCESS,
        )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return {
            "access": access_token,
            "refresh": refresh_token,
            "user_id": str(user.id),
            "okj_id": user.okj_id,
            "role": user.role,
        }

    @classmethod
    @transaction.atomic
    def logout_device(cls, user: User, device_id: str, refresh_token: Optional[str] = None) -> None:
        """Joriy seans / qurilmadan chiqish (Logout)."""
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        UserDevice.objects.filter(user=user, device_id=device_id).update(is_active=False)

    @classmethod
    @transaction.atomic
    def logout_all_devices(cls, user: User) -> int:
        """Barcha qurilmalardan chiqish (Logout All Devices)."""
        count = UserDevice.objects.filter(user=user, is_active=True).update(is_active=False)
        return count
