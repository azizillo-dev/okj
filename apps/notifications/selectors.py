"""
OKJ PLATFORM - NOTIFICATIONS SELECTORS (apps/notifications/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari, N+1 muammosiz va tezkor COUNT so'rovlar shu yerda bajariladi.
"""

from typing import Optional
from django.db.models import QuerySet
from shared.selectors import BaseSelector
from .models import Notification


class NotificationSelector(BaseSelector):
    """Kitobxonning bildirishnomalar qutisidan N+1 muammosiz o'qish selektori."""

    @classmethod
    def get_user_notifications(cls, user_id, is_read: Optional[bool] = None) -> QuerySet[Notification]:
        """Kitobxonga kelgan barcha faol bildirishnomalarni vaqt bo'yicha teskari tartibda yuklaydi."""
        qs = (
            Notification.objects.select_related("actor")
            .filter(recipient_id=user_id, is_deleted=False)
        )
        if is_read is not None:
            qs = qs.filter(is_read=is_read)
        return qs.order_by("-created_at")

    @classmethod
    def get_unread_count(cls, user_id) -> int:
        """Faqat o'qilmagan bildirishnomalarning tezkor soni (COUNT)."""
        return Notification.objects.filter(
            recipient_id=user_id, is_read=False, is_deleted=False
        ).count()

    @classmethod
    def get_notification_by_id(cls, notification_id, user_id) -> Optional[Notification]:
        return Notification.objects.filter(
            id=notification_id, recipient_id=user_id, is_deleted=False
        ).first()
