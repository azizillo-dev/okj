"""
OKJ PLATFORM - ACCOUNTS MODEL TESTS (apps/accounts/tests/test_models.py)
Nega bu fayl kerak: Kitobxon modellari, OKJ-ID majburiy unikalliklari
va Soft Delete mexanizmlarini avtomatlashtirilgan testlash.
"""

import pytest
from django.db import IntegrityError
from accounts.models import User, District


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_okj_id(self):
        district = District.objects.create(name="Yunusobod", region_name="Toshkent")
        user = User.objects.create_user(
            phone_number="+998901234567",
            okj_id="OKJ-10001",
            first_name="Aziz",
            district=district,
        )
        assert user.okj_id == "OKJ-10001"
        assert user.phone_number == "+998901234567"
        assert user.full_name == "Aziz"
        assert user.total_xp == 0
        assert user.is_curator is False
        assert user.is_deleted is False

    def test_unique_okj_id_constraint(self):
        User.objects.create_user(phone_number="+998901111111", okj_id="OKJ-20000")
        with pytest.raises(IntegrityError):
            User.objects.create_user(phone_number="+998902222222", okj_id="OKJ-20000")

    def test_soft_delete_user(self):
        user = User.objects.create_user(phone_number="+998903333333", okj_id="OKJ-30000")
        assert User.objects.count() == 1
        
        user.delete()  # Soft delete
        assert user.is_deleted is True
        assert user.deleted_at is not None
        
        # Standart objects menejeri o'chirilganlarni ko'rsatmasligi shart
        assert User.objects.count() == 0
        # all_objects esa ko'rsatishi shart
        assert User.all_objects.count() == 1
