"""
OKJ PLATFORM - LIBRARY MODEL TESTS (apps/library/tests/test_models.py)
"""

import pytest
from accounts.models import User
from books.models import Book
from library.models import LibraryItem


@pytest.mark.django_db
class TestLibraryModels:
    def test_user_reading_statistic_created_on_user_signup(self):
        user = User.objects.create_user(phone_number="+998901119988", okj_id="OKJ-77001")
        assert hasattr(user, "reading_statistics")
        assert user.reading_statistics.current_streak_days == 0

    def test_library_item_creation(self):
        user = User.objects.create_user(phone_number="+998901119989", okj_id="OKJ-77002")
        book = Book.objects.create(title="Alpomish", slug="alpomish", page_count=250)
        item = LibraryItem.objects.create(
            user=user,
            book=book,
            status=LibraryItem.ReadingStatus.READING,
        )
        assert str(item) == f"{user.username} — Alpomish (READING)"
