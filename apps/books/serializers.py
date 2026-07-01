"""
OKJ PLATFORM - BOOKS SERIALIZERS (apps/books/serializers.py)
Nega bu fayl kerak: Kitob ma'lumotlarini JSON formatga o'tkazish
va kiruvchi so'rovlar validatsiyasi.
"""

from rest_framework import serializers
from .models import Author, Genre, Publisher, Language, Book, BookEdition, BookCover


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name", "slug", "bio", "birth_year", "death_year", "avatar_url")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "slug", "description")


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ("id", "name", "slug", "country", "website")


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ("id", "code", "name", "native_name")


class BookCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCover
        fields = ("id", "cover_url", "caption", "is_primary")


class BookReadSerializer(serializers.ModelSerializer):
    """Kitobni o'qish uchun to'liq serializer (Author, Genre, Publisher o'ralgan)."""
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "original_title",
            "subtitle",
            "description",
            "isbn_13",
            "isbn_10",
            "slug",
            "publication_year",
            "page_count",
            "language",
            "publisher",
            "authors",
            "genres",
            "cover_image",
            "average_rating",
            "ratings_count",
            "reviews_count",
            "reading_count",
            "favorites_count",
            "verification_status",
            "created_at",
        )


class BookWriteSerializer(serializers.Serializer):
    """Kitob yaratish va tahrirlash uchun payload."""
    title = serializers.CharField(max_length=300)
    original_title = serializers.CharField(max_length=300, required=False, allow_blank=True)
    subtitle = serializers.CharField(max_length=300, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    isbn_13 = serializers.CharField(max_length=17, required=False, allow_blank=True, allow_null=True)
    isbn_10 = serializers.CharField(max_length=13, required=False, allow_blank=True, allow_null=True)
    publication_year = serializers.IntegerField(required=False, allow_null=True)
    page_count = serializers.IntegerField(required=False, allow_null=True)
    language_id = serializers.IntegerField(required=False, allow_null=True)
    publisher_id = serializers.IntegerField(required=False, allow_null=True)
    genre_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    author_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    cover_image = serializers.URLField(max_length=500, required=False, allow_blank=True)
    search_keywords = serializers.CharField(max_length=500, required=False, allow_blank=True)
