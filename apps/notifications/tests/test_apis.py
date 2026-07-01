"""
OKJ PLATFORM - NOTIFICATIONS API TESTS (apps/notifications/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.services import UserService
from notifications.services import NotificationService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestNotificationsAPI:
    def test_inbox_unread_count_and_read_all(self, api_client):
        user = UserService.register_reader(phone_number="+998905556681")
        api_client.force_authenticate(user=user)

        notif = NotificationService.create_notification(
            recipient_id=user.id,
            actor_id=None,
            notification_type="SYSTEM",
            text="Test xabar",
        )

        # 1. Unread count
        resp_count = api_client.get("/api/v1/notifications/unread-count/")
        assert resp_count.status_code == status.HTTP_200_OK
        assert resp_count.json()["data"]["unread_count"] == 1

        # 2. Inbox ro'yxat
        resp_inbox = api_client.get("/api/v1/notifications/")
        assert resp_inbox.status_code == status.HTTP_200_OK
        assert len(resp_inbox.json()["data"]["results"]) == 1

        # 3. Read single
        resp_read = api_client.post(f"/api/v1/notifications/{notif.id}/read/")
        assert resp_read.status_code == status.HTTP_200_OK

        # 4. Read all
        resp_read_all = api_client.post("/api/v1/notifications/read-all/")
        assert resp_read_all.status_code == status.HTTP_200_OK
