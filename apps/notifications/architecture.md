# OKJ Platform — Notifications Module Architecture (`apps/notifications/`)

This document serves as the structural reference for the **Centralized Asynchronous Notifications Module**, providing real-time engagement alerts across the **O'zbekiston Kitobxonlari Jamiyati (OKJ)** ecosystem.

---

## 1. Event-Driven Decoupling via Celery

To adhere strictly to the **Modular Monolith** pattern:
Core transactional domains (`posts`, `interactions`, `comments`, `follows`, `library`) must never stall HTTP response times to write notifications synchronously.
Instead, when an event occurs (e.g., User A likes User B's post), the interaction service invokes the decoupled Celery task:
```python
from notifications.tasks import create_notification_task
create_notification_task.delay(
    recipient_id=post.user_id,
    actor_id=user.id,
    notification_type="LIKE",
    text="Sizning postingizga layk bosdi",
    target_id=post.id
)
```
This guarantees $O(1)$ API latency for the interacting user while background workers process notification delivery asynchronously.

---

## 2. High-Density Inbox Indexing (`idx_notif_inbox`)

An active reader's notification inbox is queried repeatedly on every screen load or poll.
To prevent full table scans over millions of historical notification rows, `Notification` declares a specialized B-Tree composite index:
```python
models.Index(fields=["recipient", "is_read", "is_deleted", "-created_at"], name="idx_notif_inbox")
```
This single index covers filtering by recipient, read status, and soft-delete state while providing pre-sorted chronological ordering (`-created_at`).

---

## 3. High-Performance Bulk Operations (`mark_all_as_read`)

Iterating over ORM instances in a Python loop to mark unread notifications (`for n in unread: n.save()`) results in $O(N)$ database roundtrips.
Instead, `NotificationService.mark_all_as_read` executes an atomic bulk UPDATE:
```python
Notification.objects.filter(recipient=user, is_read=False, is_deleted=False).update(
    is_read=True, read_at=timezone.now()
)
```
This executes in a single database command regardless of whether the user has 5 or 5,000 unread alerts.
