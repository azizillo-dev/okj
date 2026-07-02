"""
OKJ PLATFORM - BOOKS MODEL TESTS (apps/books/tests/test_models.py)
"""

import pytest
from django.core.exceptions import ValidationError
from books.models import Book, Author, Genre


@pytest.mark.django_db
class TestBookModels:
    def test_author_and_genre_creation(self):
        author = Author.objects.create(name="Abdulla Qodiriy", slug="abdulla-qodiriy")
        genre = Genre.objects.create(name="Tarixiy Roman", slug="tarixiy-roman")
        assert str(author) == "Abdulla Qodiriy"
        assert str(genre) == "Tarixiy Roman"

    def test_book_creation_and_statistics_signal(self):
        book = Book.objects.create(
            title="O'tkan kunlar",
            slug="otkan-kunlar",
            isbn_13="9789943012345",
            publication_year=1926,
            page_count=400,
        )
        assert str(book) == "O'tkan kunlar"
        # Signal ishlaganini tekshiramiz
        assert hasattr(book, "statistics")
        assert book.statistics.popularity_score == 0.0

    def test_isbn_validation(self):
        book = Book(title="Test Book", slug="test-book", isbn_13="123")
        with pytest.raises(ValidationError):
            book.full_clean()
