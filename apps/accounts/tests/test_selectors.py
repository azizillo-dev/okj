"""
OKJ PLATFORM - ACCOUNTS SELECTOR TESTS (apps/accounts/tests/test_selectors.py)
"""

import pytest
from accounts.models import User, District
from accounts.selectors import UserSelector, DistrictSelector


@pytest.mark.django_db
class TestUserSelector:
    def test_get_user_by_okj_id(self):
        User.objects.create_user(phone_number="+998904444444", okj_id="OKJ-40000")
        found = UserSelector.get_user_by_okj_id("OKJ-40000")
        assert found is not None
        assert found.phone_number == "+998904444444"

    def test_get_district_leaderboard(self):
        district = District.objects.create(name="Chilonzor", region_name="Toshkent")
        User.objects.create_user(phone_number="+998905555551", okj_id="OKJ-50001", district=district, total_xp=100)
        User.objects.create_user(phone_number="+998905555552", okj_id="OKJ-50002", district=district, total_xp=300)
        
        leaders = UserSelector.get_district_leaderboard(district.id)
        assert len(leaders) == 2
        assert leaders[0].okj_id == "OKJ-50002"  # 300 XP birinchi o'rinda
