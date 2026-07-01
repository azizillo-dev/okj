"""
OKJ PLATFORM - BOOKS SERVICE TESTS (apps/books/tests/test_services.py)
"""

import pytest
from core.exceptions import ApplicationError
from books.models import Book
from books.services import BookService


@pytest.mark.django_db
class TestBookService:
    def test_create_book_auto_slug(self):
        book = BookService.create_book(title="Yulduzli Tunlar", isbn_13="9789943000001")
        assert book.slug == "yulduzli-tunlar"
        assert book.verification_status == Book.VerificationStatus.DRAFT

    def test_create_book_prevent_duplicate_isbn(self):
        BookService.create_book(title="Kitob 1", isbn_13="9789943000002")
        with pytest.raises(ApplicationError):
            BookService.create_book(title="Kitob 2", isbn_13="9789943000002")

    def test_verify_and_soft_delete(self):
        book = BookService.create_book(title="Ulug'bek Xazinasi")
        BookService.verify_book(book)
        assert book.verification_status == Book.VerificationStatus.VERIFIED

        BookService.soft_delete_book(book)
        assert Book.objects.count() == 0
        assert Book.all_objects.count() == 1
