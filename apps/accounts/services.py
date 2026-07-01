"""
OKJ PLATFORM - ACCOUNTS SERVICES (apps/accounts/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH (INSERT/UPDATE)
amallari faqat shu servislar ichida bajariladi. Tranzaksiya (`transaction.atomic()`)
va biznes qoidalar shu yerda 100% nazorat qilinadi.
"""

import random
from typing import Optional
from django.db import transaction
from django.db.models import F
from core.exceptions import ApplicationError
from core.utils import generate_okj_id
from shared.services import BaseService
from .models import User, District
from .selectors import UserSelector


class UserService(BaseService):
    """Kitobxon hisobini yaratish, tahrirlash va gamifikasiya kechlarini boshqaruvchi servis."""

    @classmethod
    @transaction.atomic
    def register_reader(
        cls,
        phone_number: str,
        first_name: str = "",
        last_name: str = "",
        district_id: Optional[int] = None,
        google_id: Optional[str] = None,
    ) -> User:
        """
        Yangi kitobxonni ro'yxatdan o'tkazish va avtomatik OKJ pasport raqamini berish.
        Nega tranzaksiya: Foydalanuvchi yaratilsa-yu pasport raqam berishda xato bo'lsa,
        bazada yarimta yozuv qolmasligi shart.
        """
        if phone_number and UserSelector.get_user_by_phone(phone_number):
            raise ApplicationError("Ushbu telefon raqami bilan kitobxon allaqachon ro'yxatdan o'tgan.")

        district = None
        if district_id:
            district = District.objects.filter(id=district_id).first()
            if not district:
                raise ApplicationError("Ko'rsatilgan tuman topilmadi.")

        # Keyingi ketma-ket raqamni topib OKJ-ID yasaymiz
        last_id = User.all_objects.count() + 10001
        okj_id = generate_okj_id(last_id)

        # Agar to'qnashuv bo'lsa, tasodifiy qo'shimcha qilamiz
        while User.all_objects.filter(okj_id=okj_id).exists():
            last_id += random.randint(1, 100)
            okj_id = generate_okj_id(last_id)

        username = phone_number or f"google_{google_id}_{last_id}"

        user = User.objects.create(
            username=username,
            phone_number=phone_number,
            google_id=google_id,
            first_name=first_name,
            last_name=last_name,
            district=district,
            okj_id=okj_id,
            role=User.Role.READER,
        )
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
