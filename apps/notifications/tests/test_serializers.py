"""
OKJ PLATFORM - NOTIFICATIONS SERIALIZER TESTS (apps/notifications/tests/test_serializers.py)
"""

import pytest
from accounts.models import User
from notifications.models import Notification, NotificationType
from notifications.serializers import NotificationReadSerializer


@pytest.mark.django_db
class TestNotificationSerializers:
    def test_notification_read_serializer(self):
        recipient = User.objects.create_user(phone_number="+998904445571", okj_id="OKJ-93007")
        actor = User.objects.create_user(phone_number="+998904445572", okj_id="OKJ-93008")
        notif = Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=NotificationType.COMMENT,
            text="Izoh yozdi",
        )

        data = NotificationReadSerializer(notif).data
        assert data["actor"]["username"] == actor.username
