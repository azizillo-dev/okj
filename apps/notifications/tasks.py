"""
OKJ PLATFORM - NOTIFICATIONS CELERY TASKS (apps/notifications/tasks.py)
Nega bu fayl kerak: Boshqa modullar (interactions, comments, follows) orqali
hodisa sodir bo'lganda, foydalanuvchini va bazani kutirmasdan asinxron ishlaydi.
"""

from typing import Optional
from celery import shared_task
from .services import NotificationService


@shared_task(name="notifications.create_notification_task")
def create_notification_task(
    recipient_id: str,
    actor_id: Optional[str],
    notification_type: str,
    text: str,
    target_id: Optional[str] = None,
):
    """
    Celery asinxron taski.
    Chaqirish namunasi (boshqa modullarning ilgaklaridan):
      from notifications.tasks import create_notification_task
      create_notification_task.delay(
          recipient_id=post.user_id,
          actor_id=user.id,
          notification_type="LIKE",
          text="Sizning postingizga layk bosdi",
          target_id=post.id
      )
    """
    notif = NotificationService.create_notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        notification_type=notification_type,
        text=text,
        target_id=target_id,
    )
    return str(notif.id) if notif else None
