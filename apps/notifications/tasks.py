"""
OKJ PLATFORM - NOTIFICATIONS CELERY TASKS (apps/notifications/tasks.py)
Nega bu fayl kerak: Boshqa modullar (interactions, comments, follows) orqali
hodisa sodir bo'lganda, foydalanuvchini va bazani kutirmasdan asinxron ishlaydi.

AUTORETRY ARXITEKTURASI:
- autoretry_for=(Exception,): Har qanday xato (DB uzilishi, network xatosi) uchun
  avtomatik qayta urinish.
- max_retries=5: Jami 5 marta urinib, keyin DLQ (Dead Letter Queue) ga o'tadi.
- retry_backoff=True: Har urinish orasida eksponansial kechikish (1s, 2s, 4s, 8s, 16s).
- retry_backoff_max=60: Kechikish 60 soniyadan oshmasin.
"""

from typing import Optional
from celery import shared_task
from .services import NotificationService


@shared_task(
    name="notifications.create_notification_task",
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=60,
)
def create_notification_task(
    recipient_id: str,
    actor_id: Optional[str],
    notification_type: str,
    text: str,
    target_id: Optional[str] = None,
):
    """
    Celery asinxron taski — bildirishnoma yaratish.

    Chaqirish namunasi (boshqa modullarning ilgaklaridan):
      from notifications.tasks import create_notification_task
      create_notification_task.delay(
          recipient_id=str(post.user_id),
          actor_id=str(user.id),
          notification_type="LIKE",
          text="Sizning postingizga layk bosdi",
          target_id=str(post.id)
      )

    Nega autoretry: Celery task bajarilayotganda DB yoki Redis vaqtincha
    ishlamay qolsa, task yo'qolmasin — eksponansial kechikish bilan qayta urinadi.
    """
    notif = NotificationService.create_notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        notification_type=notification_type,
        text=text,
        target_id=target_id,
    )
    return str(notif.id) if notif else None
