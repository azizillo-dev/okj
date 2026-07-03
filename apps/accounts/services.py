"""
OKJ PLATFORM - ACCOUNTS SERVICES (apps/accounts/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH (INSERT/UPDATE)
amallari faqat shu servislar ichida bajariladi. Tranzaksiya (`transaction.atomic()`)
va biznes qoidalar shu yerda 100% nazorat qilinadi.

OKJ_ID GENERATSIYA ARXITEKTURASI:
- okj_number: PositiveIntegerField — PostgreSQL darajasida numerik saralash uchun.
  Matnli ('OKJ-99999' vs 'OKJ-100000') lexicographical xavfi yo'q.
- select_for_update() + order_by("-okj_number"): Row-level lock orqali atomik ID.
  Parallel so'rovlar ham takrorlanmas raqam oladi.
- Okj_id = f"OKJ-{okj_number}" — inson o'qiydigan matnli format.
"""

from typing import Optional
from django.db import transaction
from django.db.models import F
from core.exceptions import ApplicationError
from shared.services import BaseService
from .models import User, District
from .selectors import UserSelector

# OKJ raqamlari 10001 dan boshlanadi (OKJ-10001 — birinchi kitobxon)
OKJ_NUMBER_START = 10001


class UserService(BaseService):
    """Kitobxon hisobini yaratish, tahrirlash va gamifikasiya kechlarini boshqaruvchi servis."""

    @classmethod
    def _generate_atomic_okj_id(cls) -> tuple[int, str]:
        """
        PostgreSQL darajasida atomik va takrorlanmas OKJ raqami va ID yaratish.

        Muammo 1 (Race Condition / TOCTOU):
        count() + 10001 mantiqi ikkita parallel so'rovda bir xil raqam beradi.

        Muammo 2 (Lexicographical Sort):
        okj_id matn sifatida saqlanganida 'OKJ-9' > 'OKJ-10' ko'rinadi, chunki
        '9' > '1'. Bu 99,999 dan o'tganda tartiblash buzilishiga olib keladi.

        Yechim (Numerical Row-Level Lock):
        - okj_number = PositiveIntegerField — haqiqiy raqam, har doim to'g'ri tartiblanadi.
        - select_for_update() bilan eng katta okj_number qatora PostgreSQL darajasida
          QULLANADI (FOR UPDATE). Shu tranzaksiya tugamaguncha boshqa biror so'rov
          shu qatorni yoki yangi qator qo'sha olmaydi.
        - Yangi okj_number = oxirgi + 1 (deterministik, tasodifiy emas).
        """
        last_user = (
            User.all_objects
            .filter(okj_number__isnull=False)
            .order_by("-okj_number")
            .select_for_update()
            .first()
        )

        if last_user and last_user.okj_number:
            next_number = last_user.okj_number + 1
        else:
            next_number = OKJ_NUMBER_START

        okj_id = f"OKJ-{next_number}"
        return next_number, okj_id

    @classmethod
    @transaction.atomic
    def register_reader(
        cls,
        phone_number: Optional[str] = None,
        first_name: str = "",
        last_name: str = "",
        district_id: Optional[int] = None,
        google_id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """
        Yangi kitobxonni ro'yxatdan o'tkazish va avtomatik OKJ pasport raqamini berish.
        """
        if phone_number and phone_number.startswith("+998") and UserSelector.get_user_by_phone(phone_number):
            raise ApplicationError("Ushbu telefon raqami bilan kitobxon allaqachon ro'yxatdan o'tgan.")

        if username and User.objects.filter(username__iexact=username).exists():
            raise ApplicationError("Ushbu foydalanuvchi nomi allaqachon band qilingan.")

        district = None
        if district_id:
            district = District.objects.filter(id=district_id).first()
            if not district:
                raise ApplicationError("Ko'rsatilgan tuman topilmadi.")

        okj_number, okj_id = cls._generate_atomic_okj_id()

        final_username = username or phone_number or email or f"user_{okj_number}"
        final_phone = phone_number if (phone_number and phone_number.startswith("+998")) else None

        user = User.objects.create(
            username=final_username,
            email=email or "",
            phone_number=final_phone,
            google_id=google_id,
            first_name=first_name,
            last_name=last_name,
            district=district,
            okj_id=okj_id,
            okj_number=okj_number,
            role=User.Role.READER,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    @classmethod
    @transaction.atomic
    def update_profile(
        cls,
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        district_id: Optional[int] = None,
    ) -> User:
        """Kitobxon profilining ma'lumotlarini tahrirlash."""
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if bio is not None:
            user.bio = bio
        if avatar_url is not None:
            user.avatar_url = avatar_url
        if district_id is not None:
            district = District.objects.filter(id=district_id).first()
            if not district:
                raise ApplicationError("Ko'rsatilgan tuman topilmadi.")
            user.district = district

        user.full_clean()
        user.save()
        return user

    @classmethod
    @transaction.atomic
    def add_xp(cls, user_id=None, amount: int = 0, user=None, reason: str = None) -> None:
        """
        Foydalanuvchining umumiy XP ballarini F() ifodasi bilan atomik oshirish.
        Nega F(): Bir vaqtda 2 ta post yozilganda ballar yo'qolib qolmasligi (Race Condition) uchun.
        """
        if amount <= 0:
            return
        target_id = user.id if user else user_id
        if not target_id:
            return
        User.objects.filter(id=target_id).update(total_xp=F("total_xp") + amount)

    @classmethod
    @transaction.atomic
    def increment_streak(cls, user_id) -> None:
        """Foydalanuvchining kunlik olovchasini 1 kunga oshirish."""
        user = User.objects.select_for_update().filter(id=user_id).first()
        if user:
            user.current_streak += 1
            if user.current_streak > user.highest_streak:
                user.highest_streak = user.current_streak
            user.save(update_fields=["current_streak", "highest_streak"])

    @classmethod
    @transaction.atomic
    def reset_streak(cls, user_id) -> None:
        """Kuni uzilib qolganda olovchani nolga tushirish."""
        User.objects.filter(id=user_id).update(current_streak=0)

    @classmethod
    @transaction.atomic
    def soft_delete_user(cls, user: User) -> None:
        """Kitobxon hisobini o'chirish (Soft Delete)."""
        user.is_active = False
        user.delete()
