"""
OKJ PLATFORM - POSTS SERIALIZERS (apps/posts/serializers.py)
Nega bu fayl kerak: Postlar, rasmlar va shikoyatlar uchun JSON
validatsiya va serializatsiya.
"""

from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from books.serializers import BookReadSerializer
from .models import Post, PostMedia


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ("id", "image_url", "caption", "order")


class PostReadSerializer(serializers.ModelSerializer):
    """Postlarni o'qish uchun serializer (User va Book, Media o'ralgan)."""
    user = UserPublicSerializer(read_only=True)
    book = BookReadSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "post_type",
            "status",
            "moderation_status",
            "visibility",
            "title",
            "content",
            "quote_text",
            "quote_page",
            "user_rating",
            "book",
            "library_item",
            "district",
            "hashtags",
            "mentions",
            "slug",
            "views_count",
            "media",
            "publish_at",
            "published_at",
            "created_at",
            "updated_at",
        )


class MediaItemWriteSerializer(serializers.Serializer):
    image_url = serializers.URLField()
    caption = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(min_value=0, default=0)


class CreatePostSerializer(serializers.Serializer):
    post_type = serializers.ChoiceField(choices=Post.PostType.choices)
    status = serializers.ChoiceField(choices=Post.Status.choices, default=Post.Status.DRAFT)
    title = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    quote_text = serializers.CharField(required=False, allow_blank=True)
    quote_page = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    user_rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)
    book_id = serializers.UUIDField(required=False, allow_null=True)
    library_item_id = serializers.UUIDField(required=False, allow_null=True)
    district_id = serializers.IntegerField(required=False, allow_null=True)
    hashtags = serializers.CharField(required=False, allow_blank=True)
    mentions = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(choices=Post.Visibility.choices, default=Post.Visibility.PUBLIC)
    publish_at = serializers.DateTimeField(required=False, allow_null=True)
    media_items = MediaItemWriteSerializer(many=True, required=False)


class UpdatePostSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    quote_text = serializers.CharField(required=False, allow_blank=True)
    quote_page = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    user_rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)
    district_id = serializers.IntegerField(required=False, allow_null=True)
    hashtags = serializers.CharField(required=False, allow_blank=True)
    mentions = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(choices=Post.Visibility.choices, required=False)
    media_items = MediaItemWriteSerializer(many=True, required=False)


class PostReportSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)
    details = serializers.CharField(required=False, allow_blank=True)
