"""
OKJ PLATFORM - BOOKS SELECTORS (apps/books/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari shu yerda markazlashadi. Barcha so'rovlarda `select_related("language", "publisher")`
va `prefetch_related("authors", "genres")` majburiy qo'llaniladi (N+1 muammoni oldini olish uchun).
"""

from typing import Optional
from django.db.models import QuerySet, Q, Count
from shared.selectors import BaseSelector
from .models import Book, Author, Genre, Publisher


class BookSelector(BaseSelector):
    """Kitoblar katalogi bilan ishlovchi selektorlar qatlami."""

    @staticmethod
    def _base_queryset() -> QuerySet[Book]:
        """Barcha o'qishlar uchun N+1 so'rovlardan xoli asosiy QuerySet."""
        return (
            Book.verified_objects.select_related("language", "publisher")
            .prefetch_related("authors", "genres")
        )

    @classmethod
    def get_book_by_id(cls, book_id) -> Optional[Book]:
        """Kitobni ID si bo'yicha bog'liq modellar bilan olish."""
        return cls._base_queryset().filter(id=book_id).first()

    @classmethod
    def get_book_by_slug(cls, slug: str) -> Optional[Book]:
        """Kitobni uning slug'i bo'yicha olish."""
        return cls._base_queryset().filter(slug=slug).first()

    @classmethod
    def get_verified_books(cls) -> QuerySet[Book]:
        """Faqat tasdiqlangan kitoblar ro'yxati."""
        return cls._base_queryset()

    @classmethod
    def search_books(
        cls,
        query: Optional[str] = None,
        genre_slug: Optional[str] = None,
        author_slug: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> QuerySet[Book]:
        """
        Qidiruv va filtrlash selektori.
        Nega kerak: Foydalanuvchilar sarlavha, muallif, ISBN yoki kalit so'zlar orqali qidiradi.
        """
        qs = cls._base_queryset()

        if query:
            cleaned_query = query.strip()
            qs = qs.filter(
                Q(title__icontains=cleaned_query)
                | Q(authors__name__icontains=cleaned_query)
                | Q(isbn_13__iexact=cleaned_query)
                | Q(isbn_10__iexact=cleaned_query)
                | Q(search_keywords__icontains=cleaned_query)
            ).distinct()

        if genre_slug:
            qs = qs.filter(genres__slug=genre_slug)

        if author_slug:
            qs = qs.filter(authors__slug=author_slug)

        if language_code:
            qs = qs.filter(language__code=language_code)

        return qs

    @classmethod
    def get_trending_books(cls, limit: int = 20) -> QuerySet[Book]:
        """
        Eng mashhur (Trending) kitoblar ro'yxati.
        Nega kerak: Bosh sahifada kitobxonlar ko'p o'qiyotgan va yuqori baholagan adabiyotlarni chiqarish.
        """
        return cls._base_queryset().order_by("-reading_count", "-average_rating")[:limit]

    @classmethod
    def get_latest_books(cls, limit: int = 20) -> QuerySet[Book]:
        """Katalogga eng oxirgi qo'shilgan tasdiqlangan yangi kitoblar."""
        return cls._base_queryset().order_by("-created_at")[:limit]

    @classmethod
    def get_books_by_district_popularity(cls, district_id: int, limit: int = 20) -> QuerySet[Book]:
        """
        Tuman bo'yicha mashhur kitoblar.
        V1 da umumiy mashhur kitoblar qaytadi, kelajakda almashinuv va oxirgi o'qilganlar ulanadi.
        """
        return cls._base_queryset().order_by("-favorites_count", "-average_rating")[:limit]


class AuthorSelector(BaseSelector):
    """Mualliflar selektori."""
    @classmethod
    def get_all_authors(cls) -> QuerySet[Author]:
        return Author.objects.all().order_by("name")


class GenreSelector(BaseSelector):
    """Janrlar selektori."""
    @classmethod
    def get_all_genres(cls) -> QuerySet[Genre]:
        return Genre.objects.all().order_by("name")
