"""
OKJ PLATFORM - NOTIFICATIONS SERVICE & TASK TESTS (apps/notifications/tests/test_services.py)
"""

import pytest
from accounts.models import User
from notifications.services import NotificationService
from notifications.tasks import create_notification_task
from notifications.models import Notification


@pytest.mark.django_db
class TestNotificationService:
    def test_create_notification_task_and_mark_all_read(self):
        recipient = User.objects.create_user(phone_number="+998903334471", okj_id="OKJ-93004")
        actor = User.objects.create_user(phone_number="+998903334472", okj_id="OKJ-93005")

        # 1. Celery taskini sinab ko'ramiz (apply yordamida sinxron chaqirib)
        task_res = create_notification_task.apply(kwargs={
            "recipient_id": str(recipient.id),
            "actor_id": str(actor.id),
            "notification_type": "FOLLOW",
            "text": "Sizga obuna bo'ldi",
        })
        assert task_res.result is not None
        assert Notification.objects.filter(recipient=recipient, is_read=False).count() == 1

        # Yana bitta xabar qo'shamiz
        NotificationService.create_notification(
            recipient_id=recipient.id,
            actor_id=None,
            notification_type="SYSTEM",
            text="Tizim xabari",
        )
        assert Notification.objects.filter(recipient=recipient, is_read=False).count() == 2

        # 2. Bulk mark_all_as_read
        updated = NotificationService.mark_all_as_read(recipient)
        assert updated == 2
        assert Notification.objects.filter(recipient=recipient, is_read=False).count() == 0

    def test_self_notification_prevention(self):
        user = User.objects.create_user(phone_number="+998903334473", okj_id="OKJ-93006")
        notif = NotificationService.create_notification(
            recipient_id=user.id,
            actor_id=user.id,
            notification_type="LIKE",
            text="O'ziga layk bosdi",
        )
        assert notif is None
