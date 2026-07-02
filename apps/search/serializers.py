"""
OKJ PLATFORM - SEARCH SERIALIZERS (apps/search/serializers.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha API transport qatlami (Serializer)
ma'lumotlarni shakllantirishi va transport qilishi shart. Views esa Thin View bo'lishi kerak.
"""

from rest_framework import serializers
from books.models import Book
from accounts.models import User
from posts.models import Post


class BookSearchResultSerializer(serializers.ModelSerializer):
    """Kitob qidiruv natijalari uchun serializer."""
    authors = serializers.SerializerMethodField()
    similarity_score = serializers.FloatField(read_only=True, default=0.0)

    class Meta:
        model = Book
        fields = ("id", "title", "isbn_10", "isbn_13", "slug", "authors", "similarity_score")

    def get_authors(self, obj) -> list:
        # prefetch_related("authors") ishlatilgani uchun xotiradan (cache'dan) o'qiyadi
        return [author.name for author in obj.authors.all()]


class UserSearchResultSerializer(serializers.ModelSerializer):
    """Kitobxon qidiruv natijalari uchun serializer."""
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "level")

    def get_level(self, obj) -> int:
        # level = total_xp // 100
        return (getattr(obj, "total_xp", 0) or 0) // 100


class PostSearchResultSerializer(serializers.ModelSerializer):
    """Post qidiruv natijalari uchun serializer."""
    text = serializers.SerializerMethodField()
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "post_type", "text", "user", "created_at")

    def get_text(self, obj) -> str:
        if obj.post_type == Post.PostType.QUOTE:
            return (obj.quote_text or "")[:150]
        return (obj.content or "")[:150]
