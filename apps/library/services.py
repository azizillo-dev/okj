"""
OKJ PLATFORM - LIBRARY SERVICES (apps/library/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari
va olovchani (streak) hisoblash, challenge taraqqiyotini yangilash mantiqlari
faqat shu yerda @transaction.atomic ostida bajariladi.
"""

from datetime import timedelta
from typing import Optional
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from core.exceptions import ApplicationError
from books.selectors import BookSelector
from shared.services import BaseService
from .models import LibraryItem, ReadingLog, UserReadingStatistic, ReadingGoal


class LibraryService(BaseService):
    """Kitobxonning shaxsiy kutubxonasi va o'qish faolligini boshqarish servisi."""

    @classmethod
    @transaction.atomic
    def add_to_shelf(
        cls,
        user,
        book_id: str,
        status: str = LibraryItem.ReadingStatus.WANT_TO_READ,
        is_favorite: bool = False,
        notes: str = "",
    ) -> LibraryItem:
        """
        Kitobni javonga qo'shish yoki uning statusini yangilash.
        """
        book = BookSelector.get_book_by_id(book_id)
        if not book:
            raise ApplicationError("Kitob topilmadi.")

        item, created = LibraryItem.objects.get_or_create(
            user=user,
            book=book,
            defaults={
                "status": status,
                "is_favorite": is_favorite,
                "notes": notes,
                "started_at": timezone.now() if status == LibraryItem.ReadingStatus.READING else None,
                "finished_at": timezone.now() if status == LibraryItem.ReadingStatus.FINISHED else None,
            },
        )

        if not created:
            return cls.update_shelf_item(item=item, status=status, is_favorite=is_favorite, notes=notes)

        # Agar qo'shilgan zahoti FINISHED bo'lsa, statistika va challenge lar yangilanadi
        if status == LibraryItem.ReadingStatus.FINISHED:
            cls._update_stats_on_book_finished(user=user, book=book)

        return item

    @classmethod
    @transaction.atomic
    def update_shelf_item(
        cls,
        item: LibraryItem,
        status: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        user_rating: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> LibraryItem:
        """Javondagi kitob holati, sevimlilik yoki bahosini yangilash."""
        old_status = item.status

        if status is not None and status != old_status:
            item.status = status
            if status == LibraryItem.ReadingStatus.READING and not item.started_at:
                item.started_at = timezone.now()
            elif status == LibraryItem.ReadingStatus.FINISHED:
                item.finished_at = timezone.now()
                if item.book.page_count:
                    item.current_page = item.book.page_count
                cls._update_stats_on_book_finished(user=item.user, book=item.book)

        if is_favorite is not None:
            item.is_favorite = is_favorite
        if user_rating is not None:
            item.user_rating = user_rating
        if notes is not None:
            item.notes = notes

        item.full_clean()
        item.save()
        return item

    @classmethod
    @transaction.atomic
    def remove_from_shelf(cls, item: LibraryItem) -> None:
        """Kitobni javondan o'chirish."""
        item.delete()

    @classmethod
    @transaction.atomic
    def log_reading_progress(
        cls,
        user,
        library_item: LibraryItem,
        pages_read: int,
        minutes_spent: int = 0,
        note: str = "",
    ) -> ReadingLog:
        """
        Kunlik o'qish logi yozish va olovchani (streak) hisoblash.
        Nega tranzaksiya: Log yozilganda kitobning joriy sahifasi, foydalanuvchi XP si
        va 1-to-1 statistika bir vaqtda xatosiz yangilanishi shart.
        """
        if library_item.user != user:
            raise ApplicationError("Bu kitob sizning javoningizda emas.")

        today = timezone.now().date()
        log = ReadingLog.objects.create(
            library_item=library_item,
            user=user,
            pages_read=pages_read,
            minutes_spent=minutes_spent,
            log_date=today,
            note=note,
        )

        # Sahifani oshiramiz
        new_page = library_item.current_page + pages_read
        if library_item.book.page_count and new_page >= library_item.book.page_count:
            library_item.current_page = library_item.book.page_count
            cls.update_shelf_item(item=library_item, status=LibraryItem.ReadingStatus.FINISHED)
        else:
            library_item.current_page = new_page
            if library_item.status != LibraryItem.ReadingStatus.READING:
                library_item.status = LibraryItem.ReadingStatus.READING
                if not library_item.started_at:
                    library_item.started_at = timezone.now()
            library_item.save(update_fields=["current_page", "status", "started_at"])

        # Olovcha (Streak) va statistikani yangilash
        cls._update_user_streak_and_stats(user=user, pages_read=pages_read, minutes_spent=minutes_spent, log_date=today)

        return log

    @classmethod
    def _update_user_streak_and_stats(cls, user, pages_read: int, minutes_spent: int, log_date):
        """Kitobxonning olovchasi (Streak) va umumiy sahifalar sonini hisoblash."""
        stats, _ = UserReadingStatistic.objects.select_for_update().get_or_create(user=user)
        stats.total_pages_read = F("total_pages_read") + pages_read
        stats.total_minutes_spent = F("total_minutes_spent") + minutes_spent

        yesterday = log_date - timedelta(days=1)
        if stats.last_log_date == log_date:
            pass  # Bugun allaqachon yozilgan
        elif stats.last_log_date == yesterday:
            stats.current_streak_days = F("current_streak_days") + 1
            stats.last_log_date = log_date
        else:
            stats.current_streak_days = 1
            stats.last_log_date = log_date

        stats.save()
        stats.refresh_from_db()
        if stats.current_streak_days > stats.longest_streak_days:
            stats.longest_streak_days = stats.current_streak_days
            stats.save(update_fields=["longest_streak_days"])

        # Kitobxonning XP sini oshirish (Har 1 sahifa = 5 XP)
        from accounts.services import UserService
        UserService.add_xp(user=user, amount=pages_read * 5, reason="Kitob o'qish (Reading progress)")

    @classmethod
    def _update_stats_on_book_finished(cls, user, book):
        """Kitob o'qib tugatilganda statistikani va challengelarni yangilash."""
        stats, _ = UserReadingStatistic.objects.select_for_update().get_or_create(user=user)
        stats.total_books_finished = F("total_books_finished") + 1
        stats.save(update_fields=["total_books_finished"])

        current_year = timezone.now().year
        current_month = timezone.now().month

        ReadingGoal.objects.filter(
            user=user, period_type=ReadingGoal.PeriodType.YEARLY, target_year=current_year
        ).update(completed_books=F("completed_books") + 1)

        ReadingGoal.objects.filter(
            user=user, period_type=ReadingGoal.PeriodType.MONTHLY, target_year=current_year, target_month=current_month
        ).update(completed_books=F("completed_books") + 1)

    @classmethod
    @transaction.atomic
    def create_or_update_goal(
        cls,
        user,
        period_type: str,
        target_year: int,
        target_month: Optional[int] = None,
        target_books: int = 12,
        target_pages: int = 0,
    ) -> ReadingGoal:
        """Yillik yoki oylik o'qish maqsadi (Challenge) o'rnatish."""
        goal, _ = ReadingGoal.objects.update_or_create(
            user=user,
            period_type=period_type,
            target_year=target_year,
            target_month=target_month if period_type == ReadingGoal.PeriodType.MONTHLY else None,
            defaults={
                "target_books": target_books,
                "target_pages": target_pages,
            },
        )
        return goal
