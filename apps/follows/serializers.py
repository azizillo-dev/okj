"""
OKJ PLATFORM - FOLLOWS SERIALIZERS (apps/follows/serializers.py)
Nega bu fayl kerak: Obunalar va obunachilar ro'yxati uchun JSON serializatsiya.
"""

from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from .models import Follow


class FollowerReadSerializer(serializers.ModelSerializer):
    """Foydalanuvchining obunachisi (Follower) haqida ma'lumot."""
    follower = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "follower", "created_at")


class FollowingReadSerializer(serializers.ModelSerializer):
    """Foydalanuvchi kuzatayotgan (Following) shaxs haqida ma'lumot."""
    following = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "following", "created_at")
