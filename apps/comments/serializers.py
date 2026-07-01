"""
OKJ PLATFORM - COMMENTS SERIALIZERS (apps/comments/serializers.py)
Nega bu fayl kerak: Izohlar va javoblar daraxti uchun JSON serializatsiya.
O'chirilgan izohlar serializerda "Bu izoh muallif tomonidan o'chirilgan"
ko'rinishida interpretatsiya qilinadi.
"""

from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from .models import Comment


class CommentReplySerializer(serializers.ModelSerializer):
    """Javob izohlar (Replies) uchun serializer."""
    user = UserPublicSerializer(read_only=True)
    text = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "user", "parent", "text", "is_deleted", "created_at", "updated_at")

    def get_text(self, obj: Comment) -> str:
        if obj.is_deleted:
            return "Bu izoh muallif tomonidan o'chirilgan"
        return obj.text


class CommentReadSerializer(serializers.ModelSerializer):
    """Asosiy izohlar (Root Comments) va ularning javoblari (Replies) uchun serializer."""
    user = UserPublicSerializer(read_only=True)
    text = serializers.SerializerMethodField()
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "post", "text", "is_deleted", "replies", "created_at", "updated_at")

    def get_text(self, obj: Comment) -> str:
        if obj.is_deleted:
            return "Bu izoh muallif tomonidan o'chirilgan"
        return obj.text


class CommentWriteSerializer(serializers.Serializer):
    """Yangi izoh yoki tahrirlash uchun serializer."""
    text = serializers.CharField(max_length=1000)
    parent_id = serializers.UUIDField(required=False, allow_null=True)
