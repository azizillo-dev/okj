"""
OKJ PLATFORM - NOTIFICATIONS MODEL TESTS (apps/notifications/tests/test_models.py)
"""

import pytest
from accounts.models import User
from notifications.models import Notification, NotificationType


@pytest.mark.django_db
class TestNotificationsModels:
    def test_notification_creation_and_str(self):
        recipient = User.objects.create_user(phone_number="+998901112251", okj_id="OKJ-93001")
        actor = User.objects.create_user(phone_number="+998901112252", okj_id="OKJ-93002")

        notif = Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=NotificationType.LIKE,
            text="Layk bosdi",
        )
        assert "To" in str(notif)
        assert notif.is_read is False
