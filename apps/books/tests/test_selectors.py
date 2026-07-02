"""
OKJ PLATFORM - BOOKS SELECTOR TESTS (apps/books/tests/test_selectors.py)
"""

import pytest
from books.models import Book
from books.selectors import BookSelector


@pytest.mark.django_db
class TestBookSelector:
    def test_search_books_by_title_and_keyword(self):
        book = Book.objects.create(
            title="Mehrobdan Chayon",
            slug="mehrobdan-chayon",
            search_keywords="anvar ra'no xudoyorxon",
            verification_status=Book.VerificationStatus.VERIFIED,
        )
        found = BookSelector.search_books(query="ra'no")
        assert len(found) == 1
        assert found[0].id == book.id

    def test_unverified_book_not_in_search(self):
        Book.objects.create(
            title="Qoralama Kitob",
            slug="qoralama-kitob",
            verification_status=Book.VerificationStatus.DRAFT,
        )
        found = BookSelector.search_books(query="Qoralama")
        assert len(found) == 0
