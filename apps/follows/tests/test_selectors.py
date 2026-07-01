"""
OKJ PLATFORM - FOLLOWS SELECTOR TESTS (apps/follows/tests/test_selectors.py)
"""

import pytest
from accounts.models import User
from follows.models import Follow
from follows.selectors import FollowSelector


@pytest.mark.django_db
class TestFollowSelector:
    def test_get_followers_and_following(self):
        user1 = User.objects.create_user(phone_number="+998902223351", okj_id="OKJ-92004")
        user2 = User.objects.create_user(phone_number="+998902223352", okj_id="OKJ-92005")

        Follow.objects.create(follower=user1, following=user2)

        followers = FollowSelector.get_followers(user2.id)
        assert len(followers) == 1
        assert followers[0].follower == user1

        following = FollowSelector.get_following(user1.id)
        assert len(following) == 1
        assert following[0].following == user2

        assert FollowSelector.is_following(user1, user2.id) is True
