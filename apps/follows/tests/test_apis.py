"""
OKJ PLATFORM - FOLLOWS API TESTS (apps/follows/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.services import UserService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestFollowsAPI:
    def test_follow_toggle_and_list_api(self, api_client):
        user1 = UserService.register_reader(phone_number="+998905556671")
        user2 = UserService.register_reader(phone_number="+998905556672")
        api_client.force_authenticate(user=user1)

        # Obuna bo'lamiz
        resp_follow = api_client.post(f"/api/v1/users/{user2.id}/follow/")
        assert resp_follow.status_code == status.HTTP_201_CREATED

        # Obunachilar ro'yxatini o'qiymiz
        resp_list = api_client.get(f"/api/v1/users/{user2.id}/followers/")
        assert resp_list.status_code == status.HTTP_200_OK
        assert len(resp_list.json()["data"]) == 1

        # Obunani bekor qilamiz
        resp_unfollow = api_client.delete(f"/api/v1/users/{user2.id}/unfollow/")
        assert resp_unfollow.status_code == status.HTTP_200_OK
