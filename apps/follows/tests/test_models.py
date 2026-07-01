"""
OKJ PLATFORM - FOLLOWS MODEL TESTS (apps/follows/tests/test_models.py)
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from accounts.models import User
from follows.models import Follow


@pytest.mark.django_db
class TestFollowsModels:
    def test_follow_creation_and_string_representation(self):
        user1 = User.objects.create_user(phone_number="+998901112241", okj_id="OKJ-92001")
        user2 = User.objects.create_user(phone_number="+998901112242", okj_id="OKJ-92002")

        follow = Follow.objects.create(follower=user1, following=user2)
        assert str(follow) == f"{user1.username} ➡️ {user2.username}"

    def test_self_follow_prevention_clean(self):
        user = User.objects.create_user(phone_number="+998901112243", okj_id="OKJ-92003")
        follow = Follow(follower=user, following=user)
        with pytest.raises(ValidationError):
            follow.full_clean()
