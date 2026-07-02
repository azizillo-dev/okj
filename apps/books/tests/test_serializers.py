"""
OKJ PLATFORM - BOOKS SERIALIZER TESTS (apps/books/tests/test_serializers.py)
"""

from books.serializers import BookWriteSerializer


class TestBookSerializers:
    def test_book_write_serializer_valid(self):
        data = {
            "title": "Dunyoning ishlari",
            "publication_year": 1982,
            "page_count": 210,
        }
        serializer = BookWriteSerializer(data=data)
        assert serializer.is_valid() is True

    def test_book_write_serializer_missing_title(self):
        data = {"publication_year": 1982}
        serializer = BookWriteSerializer(data=data)
        assert serializer.is_valid() is False
        assert "title" in serializer.errors
