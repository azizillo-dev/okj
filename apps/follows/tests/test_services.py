"""
OKJ PLATFORM - FOLLOWS SERVICE TESTS (apps/follows/tests/test_services.py)
"""

import pytest
from core.exceptions import ApplicationError
from accounts.models import User
from follows.services import FollowService
from follows.models import Follow


@pytest.mark.django_db
class TestFollowService:
    def test_follow_toggle_and_row_reuse(self):
        user1 = User.objects.create_user(phone_number="+998903334461", okj_id="OKJ-92006")
        user2 = User.objects.create_user(phone_number="+998903334462", okj_id="OKJ-92007")

        # 1. Obuna bo'lamiz
        f1, created1 = FollowService.toggle_follow(follower=user1, following_id=user2.id)
        assert created1 is True
        assert Follow.objects.filter(follower=user1, following=user2, is_deleted=False).count() == 1
        user1.refresh_from_db()
        assert user1.total_xp == 5  # Gamification +5 XP

        # 2. Bekor qilamiz (Unlike/Soft delete)
        f2, created2 = FollowService.toggle_follow(follower=user1, following_id=user2.id)
        assert created2 is False
        assert Follow.objects.filter(follower=user1, following=user2, is_deleted=False).count() == 0

        # 3. Yana obuna bo'lamiz (O(1) Row Reuse)
        f3, created3 = FollowService.toggle_follow(follower=user1, following_id=user2.id)
        assert created3 is True
        assert f3.id == f1.id
        assert Follow.objects.filter(follower=user1, following=user2, is_deleted=False).count() == 1

    def test_self_follow_raises_application_error(self):
        user = User.objects.create_user(phone_number="+998903334463", okj_id="OKJ-92008")
        with pytest.raises(ApplicationError) as exc_info:
            FollowService.follow_user(follower=user, following_id=user.id)
        assert exc_info.value.code == "SELF_FOLLOW_DENIED"
