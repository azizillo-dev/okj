"""
OKJ PLATFORM - NOTIFICATIONS SERVICES (apps/notifications/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari,
o'qilgan deb belgilash va ommaviy Bulk UPDATE amallari @transaction.atomic ostida.
"""

from typing import Optional
from django.db import transaction
from django.utils import timezone
from core.exceptions import ApplicationError
from shared.services import BaseService
from .models import Notification


class NotificationService(BaseService):
    """Bildirishnomalar yaratish va ularning holatini boshqarish servisi."""

    @classmethod
    @transaction.atomic
    def create_notification(
        cls,
        recipient_id,
        actor_id: Optional[str],
        notification_type: str,
        text: str,
        target_id: Optional[str] = None,
    ) -> Notification:
        """
        Yangi bildirishnoma yaratish. Ushbu metod ko'pincha Celery asinxron
        task orqali chaqiriladi. O'z-o'ziga bildirishnoma jo'natilmaydi.
        """
        if actor_id and str(recipient_id) == str(actor_id):
            return None

        return Notification.objects.create(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=notification_type,
            target_id=target_id,
            text=text,
        )

    @classmethod
    @transaction.atomic
    def mark_as_read(cls, user, notification_id) -> Notification:
        """Bitta bildirishnomani o'qilgan holatga o'tkazish."""
        notif = Notification.objects.filter(
            id=notification_id, recipient=user, is_deleted=False
        ).first()
        if not notif:
            raise ApplicationError("Bildirishnoma topilmadi.", code="NOTIFICATION_NOT_FOUND")

        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at", "updated_at"])
        return notif

    @classmethod
    @transaction.atomic
    def mark_all_as_read(cls, user) -> int:
        """
        Kitobxonning barcha o'qilmagan bildirishnomalarini bitta toza
        Bulk UPDATE so'rovi orqali o'qilgan holatga o'tkazish.
        Qaytadi: yangilangan qatorlar soni.
        """
        updated_count = Notification.objects.filter(
            recipient=user, is_read=False, is_deleted=False
        ).update(is_read=True, read_at=timezone.now())
        return updated_count
