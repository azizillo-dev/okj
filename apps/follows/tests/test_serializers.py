"""
OKJ PLATFORM - FOLLOWS SERIALIZER TESTS (apps/follows/tests/test_serializers.py)
"""

import pytest
from accounts.models import User
from follows.models import Follow
from follows.serializers import FollowerReadSerializer


@pytest.mark.django_db
class TestFollowSerializers:
    def test_follower_read_serializer(self):
        user1 = User.objects.create_user(phone_number="+998904445561", okj_id="OKJ-92009")
        user2 = User.objects.create_user(phone_number="+998904445562", okj_id="OKJ-92010")
        follow = Follow.objects.create(follower=user1, following=user2)

        data = FollowerReadSerializer(follow).data
        assert data["follower"]["username"] == user1.username
