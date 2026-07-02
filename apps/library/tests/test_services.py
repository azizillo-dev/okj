"""
OKJ PLATFORM - LIBRARY SERVICE TESTS (apps/library/tests/test_services.py)
"""

import pytest
from accounts.models import User
from books.models import Book
from library.models import LibraryItem, ReadingGoal
from library.services import LibraryService
from library.selectors import LibrarySelector


@pytest.mark.django_db
class TestLibraryService:
    def test_add_to_shelf_and_log_progress(self):
        user = User.objects.create_user(phone_number="+998903337766", okj_id="OKJ-77004")
        book = Book.objects.create(title="Sariq devni minib", slug="sariq-devni-minib", page_count=200, verification_status="VERIFIED")

        item = LibraryService.add_to_shelf(user=user, book_id=str(book.id), status=LibraryItem.ReadingStatus.READING)
        assert item.current_page == 0

        # Progress log yozamiz
        log = LibraryService.log_reading_progress(user=user, library_item=item, pages_read=50, minutes_spent=45)
        assert log.pages_read == 50
        item.refresh_from_db()
        assert item.current_page == 50

        # Streak va statistika nazorati
        stats = LibrarySelector.get_user_statistics(user.id)
        assert stats.total_pages_read == 50
        assert stats.current_streak_days == 1

    def test_create_or_update_goal(self):
        user = User.objects.create_user(phone_number="+998904446655", okj_id="OKJ-77005")
        goal = LibraryService.create_or_update_goal(
            user=user,
            period_type=ReadingGoal.PeriodType.YEARLY,
            target_year=2026,
            target_books=24,
        )
        assert goal.target_books == 24
