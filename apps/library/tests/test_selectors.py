"""
OKJ PLATFORM - LIBRARY SELECTOR TESTS (apps/library/tests/test_selectors.py)
"""

import pytest
from django.utils import timezone
from accounts.models import User
from books.models import Book
from library.models import LibraryItem, ReadingLog
from library.selectors import LibrarySelector


@pytest.mark.django_db
class TestLibrarySelector:
    def test_get_user_shelf_filtered(self):
        user = User.objects.create_user(phone_number="+998902228877", okj_id="OKJ-77003")
        book1 = Book.objects.create(title="Kitob 1", slug="kitob-1")
        book2 = Book.objects.create(title="Kitob 2", slug="kitob-2")

        LibraryItem.objects.create(user=user, book=book1, status=LibraryItem.ReadingStatus.READING, is_favorite=True)
        LibraryItem.objects.create(user=user, book=book2, status=LibraryItem.ReadingStatus.FINISHED, is_favorite=False)

        reading_items = LibrarySelector.get_user_shelf(user.id, status=LibraryItem.ReadingStatus.READING)
        assert len(reading_items) == 1
        assert reading_items[0].book == book1

        fav_items = LibrarySelector.get_user_shelf(user.id, is_favorite=True)
        assert len(fav_items) == 1
