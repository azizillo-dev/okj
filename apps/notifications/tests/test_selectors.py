"""
OKJ PLATFORM - NOTIFICATIONS SELECTOR TESTS (apps/notifications/tests/test_selectors.py)
"""

import pytest
from accounts.models import User
from notifications.models import Notification
from notifications.selectors import NotificationSelector


@pytest.mark.django_db
class TestNotificationSelector:
    def test_unread_count_and_inbox_filter(self):
        recipient = User.objects.create_user(phone_number="+998902223361", okj_id="OKJ-93003")

        Notification.objects.create(recipient=recipient, text="Xabar 1", is_read=False)
        Notification.objects.create(recipient=recipient, text="Xabar 2", is_read=True)

        assert NotificationSelector.get_unread_count(recipient.id) == 1
        assert len(NotificationSelector.get_user_notifications(recipient.id)) == 2
        assert len(NotificationSelector.get_user_notifications(recipient.id, is_read=False)) == 1
