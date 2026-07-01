"""
OKJ PLATFORM - INTERACTIONS SERIALIZERS (apps/interactions/serializers.py)
Nega bu fayl kerak: Layklar va saqlanganlar (bookmarks) uchun JSON serializatsiya.
"""

from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from posts.serializers import PostReadSerializer
from .models import PostLike, PostBookmark


class PostLikeSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ("id", "user", "post", "created_at")


class PostBookmarkSerializer(serializers.ModelSerializer):
    post = PostReadSerializer(read_only=True)

    class Meta:
        model = PostBookmark
        fields = ("id", "post", "collection_name", "created_at")


class BookmarkCreateSerializer(serializers.Serializer):
    collection_name = serializers.CharField(max_length=100, default="Asosiy", required=False)
