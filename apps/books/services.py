"""
OKJ PLATFORM - BOOKS SERVICES (apps/books/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH (INSERT/UPDATE/DELETE)
amallari va biznes qoidalar (slug yasash, ISBN to'qnashuvini oldini olish, tranzaksiyalar)
faqat shu servislar ichida yoziladi.
"""

from typing import List, Optional
from django.db import transaction
from django.utils.text import slugify
from core.exceptions import ApplicationError
from shared.services import BaseService
from .models import Book, BookEdition, BookCover, Author, Genre, Publisher, Language, BookStatistics


class BookService(BaseService):
    """Kitoblar katalogini boshqarish servisi."""

    @classmethod
    def _generate_unique_slug(cls, title: str, book_id: Optional[str] = None) -> str:
        """
        Sarlavhadan avtomatik va takrorlanmas slug yasash.
        Nega kerak: URL larda /books/otamdan-qolgan-dalalar ko'rinishida bo'lishi va duplicat oldini olish.
        """
        base_slug = slugify(title)[:300] or "kitob"
        slug = base_slug
        counter = 1

        qs = Book.all_objects.filter(slug=slug)
        if book_id:
            qs = qs.exclude(id=book_id)

        while qs.exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            qs = Book.all_objects.filter(slug=slug)
            if book_id:
                qs = qs.exclude(id=book_id)

        return slug

    @classmethod
    @transaction.atomic
    def create_book(
        cls,
        title: str,
        isbn_13: Optional[str] = None,
        isbn_10: Optional[str] = None,
        original_title: str = "",
        subtitle: str = "",
        description: str = "",
        publication_year: Optional[int] = None,
        page_count: Optional[int] = None,
        language_id: Optional[int] = None,
        publisher_id: Optional[int] = None,
        genre_ids: Optional[List[int]] = None,
        author_ids: Optional[List[str]] = None,
        cover_image: str = "",
        search_keywords: str = "",
        is_curator: bool = False,
    ) -> Book:
        """
        Yangi kitob yozuvini yaratish.
        Agar kurator qo'shsa, avtomatik VERIFIED holatga o'tadi.
        """
        if isbn_13 and Book.all_objects.filter(isbn_13=isbn_13).exists():
            raise ApplicationError(f"ISBN-13 ({isbn_13}) raqamli kitob allaqachon mavjud.")
        if isbn_10 and Book.all_objects.filter(isbn_10=isbn_10).exists():
            raise ApplicationError(f"ISBN-10 ({isbn_10}) raqamli kitob allaqachon mavjud.")

        slug = cls._generate_unique_slug(title)
        status = Book.VerificationStatus.VERIFIED if is_curator else Book.VerificationStatus.DRAFT

        book = Book.objects.create(
            title=title,
            original_title=original_title,
            subtitle=subtitle,
            description=description,
            isbn_13=isbn_13,
            isbn_10=isbn_10,
            slug=slug,
            publication_year=publication_year,
            page_count=page_count,
            language_id=language_id,
            publisher_id=publisher_id,
            cover_image=cover_image,
            search_keywords=search_keywords,
            verification_status=status,
        )

        if genre_ids:
            book.genres.set(genre_ids)
        if author_ids:
            book.authors.set(author_ids)

        # Analitika va mashhurlik jadvalini (BookStatistics) birga yaratamiz
        BookStatistics.objects.create(book=book)

        return book

    @classmethod
    @transaction.atomic
    def update_book(cls, book: Book, **kwargs) -> Book:
        """Kitob ma'lumotlarini tahrirlash."""
        if "isbn_13" in kwargs and kwargs["isbn_13"]:
            if Book.all_objects.filter(isbn_13=kwargs["isbn_13"]).exclude(id=book.id).exists():
                raise ApplicationError("Bu ISBN-13 boshqa kitobga tegishli.")
        if "isbn_10" in kwargs and kwargs["isbn_10"]:
            if Book.all_objects.filter(isbn_10=kwargs["isbn_10"]).exclude(id=book.id).exists():
                raise ApplicationError("Bu ISBN-10 boshqa kitobga tegishli.")

        if "title" in kwargs and kwargs["title"] != book.title:
            book.slug = cls._generate_unique_slug(kwargs["title"], book_id=book.id)

        genre_ids = kwargs.pop("genre_ids", None)
        author_ids = kwargs.pop("author_ids", None)

        for field, value in kwargs.items():
            if hasattr(book, field):
                setattr(book, field, value)

        book.full_clean()
        book.save()

        if genre_ids is not None:
            book.genres.set(genre_ids)
        if author_ids is not None:
            book.authors.set(author_ids)

        return book

    @classmethod
    @transaction.atomic
    def verify_book(cls, book: Book) -> Book:
        """Kurator tomonidan kitobni tasdiqlash."""
        book.verification_status = Book.VerificationStatus.VERIFIED
        book.save(update_fields=["verification_status"])
        return book

    @classmethod
    @transaction.atomic
    def archive_book(cls, book: Book) -> Book:
        """Kitobni arxivlash."""
        book.verification_status = Book.VerificationStatus.ARCHIVED
        book.save(update_fields=["verification_status"])
        return book

    @classmethod
    @transaction.atomic
    def soft_delete_book(cls, book: Book) -> None:
        """
        Kitobni Soft Delete qilish.
        Fiziki o'chirilmaydi, chunki o'tgan yillardagi kitob almashinish tarmoqlari buzilmaydi.
        """
        book.delete()
