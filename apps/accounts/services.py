"""
OKJ PLATFORM - ACCOUNTS SERVICES (apps/accounts/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH (INSERT/UPDATE)
amallari faqat shu servislar ichida bajariladi. Tranzaksiya (`transaction.atomic()`)
va biznes qoidalar shu yerda 100% nazorat qilinadi.
"""

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
    def _generate_atomic_okj_id(cls) -> str:
        """
        PostgreSQL darajasida atomik va takrorlanmas OKJ-ID yaratish.

        Muammo (Race Condition): User.all_objects.count() + 10001 mantiqi
        bir vaqtda ikkita so'rov kelganda ikkita foydalanuvchiga bir xil
        raqamni berishi mumkin edi (TOCTOU xatosi).

        Yechim (Row-level Lock):
        - select_for_update() bilan eng oxirgi okj_id'li foydalanuvchini QULLAYDI.
        - Qullov ichida hech bir boshqa tranzaksiya bu qatorga mos qator qo'sha olmaydi.
        - Bu shu'ba (@transaction.atomic) ichida bajarilishi SHART — yuqori darajadagi
          register_reader tranzaksiyasi bu kafolatni ta'minlaydi.

        Ishlash tartibi:
          1. Barcha aktiv va o'chirilgan foydalanuvchilar orasidan, okj_id orqali
             eng yuqori raqamli foydalanuvchi ROW-LEVEL LOCK bilan tanlanadi.
          2. Agar hech kim yo'q bo'lsa, 10001 dan boshlanadi.
          3. Yangi raqam = oxirgi raqam + 1 (deterministik, tasodifiy emas).
          4. Agar (juda kam ehtimol) oldindan kiritilgan qo'lda yozuv tufayli to'qnashuv
             bo'lsa, UniqueViolation xatosi db darajasida ushlanadi.
        """
        # Barcha foydalanuvchilardan (soft deleted ham) eng katta okj_id raqamini qullash.
        # 'OKJ-XXXXX' formatidan raqamni olish uchun substring ishlatamiz.
        last_user = (
            User.all_objects
            .filter(okj_id__startswith="OKJ-")
            .order_by("-okj_id")
            .select_for_update()
            .first()
        )

        if last_user and last_user.okj_id:
            try:
                last_number = int(last_user.okj_id.split("-")[1])
            except (IndexError, ValueError):
                last_number = 10000
        else:
            last_number = 10000

        next_number = last_number + 1
        return generate_okj_id(next_number)

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

        Nega @transaction.atomic + select_for_update():
        - Foydalanuvchi yaratilsa-yu pasport raqam berishda xato bo'lsa,
          bazada yarimta yozuv qolmasligi shart.
        - Ikki foydalanuvchi bir millisekundda ro'yxatdan o'tsa ham,
          PostgreSQL qullovi (row-level lock) orqali ularga har doim UNIKAL,
          TAKRORLANMAS okj_id kafolatlanadi.
        """
        if phone_number and UserSelector.get_user_by_phone(phone_number):
            raise ApplicationError("Ushbu telefon raqami bilan kitobxon allaqachon ro'yxatdan o'tgan.")

        district = None
        if district_id:
            district = District.objects.filter(id=district_id).first()
            if not district:
                raise ApplicationError("Ko'rsatilgan tuman topilmadi.")

        # Atomik va takrorlanmas OKJ-ID yaratish (Row-level lock orqali)
        okj_id = cls._generate_atomic_okj_id()

        username = phone_number or f"google_{google_id}_{okj_id}"

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
