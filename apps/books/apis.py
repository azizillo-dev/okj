"""
OKJ PLATFORM - BOOKS API VIEWS (apps/books/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha bu viewlar YENGIL (Thin Views).
Hech qanday ORM filterlar yozilmaydi, faqat `selectors.py` va `services.py` dan foydalangan
holda JSON ma'lumotlarni qabul qilib uzatadi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from core.responses import APIResponse
from core.pagination import StandardResultsSetPagination
from .selectors import BookSelector, AuthorSelector, GenreSelector
from .services import BookService
from .permissions import IsCuratorOrReadOnly
from .serializers import (
    BookReadSerializer,
    BookWriteSerializer,
    AuthorSerializer,
    GenreSerializer,
)


class BookListCreateApi(APIView):
    """Kitoblar ro'yxatini olish (qidiruv, saralash) va yangi kitob qo'shish API."""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        query = request.query_params.get("search")
        genre_slug = request.query_params.get("genre")
        author_slug = request.query_params.get("author")
        ordering = request.query_params.get("ordering")

        books = BookSelector.search_books(query=query, genre_slug=genre_slug, author_slug=author_slug)

        if ordering == "rating":
            books = books.order_by("-average_rating")
        elif ordering == "popular":
            books = books.order_by("-reading_count")
        elif ordering == "newest":
            books = books.order_by("-created_at")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(books, request, view=self)
        serializer = BookReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BookWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_curator = getattr(request.user, "is_curator", False)
        book = BookService.create_book(is_curator=is_curator, **serializer.validated_data)
        read_serializer = BookReadSerializer(BookSelector.get_book_by_id(book.id))
        return APIResponse(
            data=read_serializer.data,
            message="Kitob muvaffaqiyatli qo'shildi.",
            status_code=status.HTTP_201_CREATED,
        )


class BookDetailApi(APIView):
    """Bitta kitobni slug bo'yicha olish, tahrirlash va o'chirish API."""
    permission_classes = [IsCuratorOrReadOnly]

    def get(self, request, slug: str):
        book = BookSelector.get_book_by_slug(slug)
        if not book:
            return APIResponse(message="Kitob topilmadi.", status_code=status.HTTP_404_NOT_FOUND)
        serializer = BookReadSerializer(book)
        return APIResponse(data=serializer.data)

    def patch(self, request, slug: str):
        book = BookSelector.get_book_by_slug(slug)
        if not book:
            return APIResponse(message="Kitob topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = BookWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_book = BookService.update_book(book=book, **serializer.validated_data)
        read_serializer = BookReadSerializer(BookSelector.get_book_by_id(updated_book.id))
        return APIResponse(data=read_serializer.data, message="Kitob ma'lumotlari yangilandi.")

    def delete(self, request, slug: str):
        book = BookSelector.get_book_by_slug(slug)
        if not book:
            return APIResponse(message="Kitob topilmadi.", status_code=status.HTTP_404_NOT_FOUND)
        BookService.soft_delete_book(book)
        return APIResponse(message="Kitob muvaffaqiyatli o'chirildi (Soft Delete).", status_code=status.HTTP_200_OK)


class TrendingBooksApi(APIView):
    """Bosh sahifa uchun eng mashhur (Trending) kitoblar API."""
    permission_classes = [AllowAny]

    def get(self, request):
        books = BookSelector.get_trending_books(limit=10)
        serializer = BookReadSerializer(books, many=True)
        return APIResponse(data=serializer.data, message="Mashhur kitoblar yuklandi.")


class AuthorListApi(APIView):
    """Barcha mualliflar ro'yxati API."""
    permission_classes = [AllowAny]

    def get(self, request):
        authors = AuthorSelector.get_all_authors()
        serializer = AuthorSerializer(authors, many=True)
        return APIResponse(data=serializer.data)


class GenreListApi(APIView):
    """Barcha janrlar ro'yxati API."""
    permission_classes = [AllowAny]

    def get(self, request):
        genres = GenreSelector.get_all_genres()
        serializer = GenreSerializer(genres, many=True)
        return APIResponse(data=serializer.data)
