"""
OKJ PLATFORM - NOTIFICATIONS SERIALIZERS (apps/notifications/serializers.py)
Nega bu fayl kerak: Bildirishnomalar va ularning yuboruvchilari haqida JSON serializatsiya.
"""

from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from .models import Notification


class NotificationReadSerializer(serializers.ModelSerializer):
    """Kirish qutisidagi bildirishnoma serializeri."""
    actor = UserPublicSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "actor",
            "notification_type",
            "target_id",
            "text",
            "is_read",
            "read_at",
            "created_at",
        )
