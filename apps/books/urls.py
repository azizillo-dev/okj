"""
OKJ PLATFORM - BOOKS URLS (apps/books/urls.py)
Nega bu fayl kerak: /api/v1/books/ ostidagi marshrutlarni aniqlash.
"""

from django.urls import path
from .apis import (
    BookListCreateApi,
    BookDetailApi,
    TrendingBooksApi,
    AuthorListApi,
    GenreListApi,
)

urlpatterns = [
    path("", BookListCreateApi.as_view(), name="book-list-create"),
    path("trending/", TrendingBooksApi.as_view(), name="book-trending"),
    path("authors/", AuthorListApi.as_view(), name="author-list"),
    path("genres/", GenreListApi.as_view(), name="genre-list"),
    path("<str:slug>/", BookDetailApi.as_view(), name="book-detail"),
]
