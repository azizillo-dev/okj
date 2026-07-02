"""
OKJ PLATFORM - LIBRARY SELECTORS (apps/library/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA O'QISH (SELECT)
amallari va N+1 muammosiz optimizatsiyalar shu yerda bajariladi.
"""

from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, Sum
from django.utils import timezone
from shared.selectors import BaseSelector
from .models import LibraryItem, ReadingLog, UserReadingStatistic, ReadingGoal


class LibrarySelector(BaseSelector):
    """Shaxsiy kutubxona va o'qish loglarini o'qish selektori."""

    @staticmethod
    def _base_shelf_queryset() -> QuerySet[LibraryItem]:
        """Kitob katalogi bog'liq jadvallarini avtomatik join qilish (N+1 oldini olish)."""
        return (
            LibraryItem.objects.select_related("book", "book__language", "book__publisher")
            .prefetch_related("book__authors", "book__genres")
        )

    @classmethod
    def get_user_shelf(
        cls,
        user_id,
        status: Optional[str] = None,
        is_favorite: Optional[bool] = None,
    ) -> QuerySet[LibraryItem]:
        """Foydalanuvchining shaxsiy javonini filtrlash."""
        qs = cls._base_shelf_queryset().filter(user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        if is_favorite is not None:
            qs = qs.filter(is_favorite=is_favorite)
        return qs

    @classmethod
    def get_library_item(cls, user_id, book_id) -> Optional[LibraryItem]:
        """Aniq bir kitob bo'yicha kutubxona yozuvini topish."""
        return cls._base_shelf_queryset().filter(user_id=user_id, book_id=book_id).first()

    @classmethod
    def get_current_reading(cls, user_id) -> QuerySet[LibraryItem]:
        """Hozir o'qilayotgan kitoblar ro'yxati."""
        return cls._base_shelf_queryset().filter(user_id=user_id, status=LibraryItem.ReadingStatus.READING)

    @classmethod
    def get_user_statistics(cls, user_id) -> UserReadingStatistic:
        """Kitobxonning statistikasi jadvalini olish yoki yordamchi saqlab berish."""
        stats, _ = UserReadingStatistic.objects.get_or_create(user_id=user_id)
        return stats

    @classmethod
    def get_reading_heatmap(cls, user_id, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        GitHub / Duolingo usulidagi yil bo'yicha kunlik faollik xaritasi (Heatmap).
        Nega kerak: Kitobxonga yil davomida qaysi kunlari qancha sahifa o'qiganini grafikda ko'rsatish.
        """
        target_year = year or timezone.now().year
        logs = (
            ReadingLog.objects.filter(user_id=user_id, log_date__year=target_year)
            .values("log_date")
            .annotate(total_pages=Sum("pages_read"), total_mins=Sum("minutes_spent"))
            .order_by("log_date")
        )
        return [
            {
                "date": log["log_date"].isoformat(),
                "pages": log["total_pages"] or 0,
                "minutes": log["total_mins"] or 0,
            }
            for log in logs
        ]

    @classmethod
    def get_user_goals(cls, user_id, year: Optional[int] = None) -> QuerySet[ReadingGoal]:
        """Kitobxonning maqsadlari (Challengelar)."""
        qs = ReadingGoal.objects.filter(user_id=user_id)
        if year:
            qs = qs.filter(target_year=year)
        return qs.order_by("-target_year", "-target_month")
