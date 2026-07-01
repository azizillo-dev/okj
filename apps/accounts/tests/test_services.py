"""
OKJ PLATFORM - ACCOUNTS SERVICE TESTS (apps/accounts/tests/test_services.py)
"""

import pytest
from core.exceptions import ApplicationError
from accounts.models import User, District
from accounts.services import UserService


@pytest.mark.django_db
class TestUserService:
    def test_register_reader_auto_okj_id(self):
        district = District.objects.create(name="Mirzo Ulug'bek", region_name="Toshkent")
        user = UserService.register_reader(
            phone_number="+998906666666",
            first_name="Alisher",
            district_id=district.id,
        )
        assert user.okj_id.startswith("OKJ-")
        assert user.role == User.Role.READER
        assert user.district == district

    def test_register_duplicate_phone_raises_error(self):
        UserService.register_reader(phone_number="+998907777777")
        with pytest.raises(ApplicationError):
            UserService.register_reader(phone_number="+998907777777")

    def test_add_xp(self):
        user = UserService.register_reader(phone_number="+998908888888")
        assert user.total_xp == 0
        
        UserService.add_xp(user.id, 50)
        user.refresh_from_db()
        assert user.total_xp == 50

    def test_increment_streak(self):
        user = UserService.register_reader(phone_number="+998909999999")
        UserService.increment_streak(user.id)
        user.refresh_from_db()
        assert user.current_streak == 1
        assert user.highest_streak == 1
