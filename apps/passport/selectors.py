"""
OKJ PLATFORM - PASSPORT SELECTORS (apps/passport/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha barcha tahliliy,
statistika va o'qish (Read) so'rovlari selektorlarda joylashishi shart.
"""

from typing import Optional, Dict, Any, List
from django.db import connections, OperationalError
from django.db.models import Count
from accounts.models import User
from library.models import UserReadingStatistic, LibraryItem
from books.models import Genre, Language


def _verify_postgres():
    """
    Twelve-Factor & Infrastructure qoidasi:
    Bu modul faqat PostgreSQL'da ishlaydi. SQLite ruxsat etilmaydi.
    """
    if connections["default"].vendor != "postgresql":
        raise OperationalError(
            "Bu modul faqat PostgreSQL'da ishlaydi. SQLite ruxsat etilmaydi."
        )


class PassportSelector:
    """Kitobxonning Elektron Pasporti va Tahliliy Tizimi selektori."""

    @classmethod
    def get_global_leaderboard_position(cls, user_id) -> int:
        """
        Kitobxonning umumiy platformadagi o'rnini (Rank) aniqlash.
        Me'moriy cheklov: Heavy Window funksiyalaridan qochish uchun,
        total_xp balli baland bo'lgan faol foydalanuvchilar sonini hisoblab (+1),
        O(log N) indeks skanerlash darajasida o'rinni topamiz.
        """
        _verify_postgres()
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return 0

        higher_xp_count = User.objects.filter(
            is_deleted=False,
            is_active=True,
            total_xp__gt=user.total_xp,
        ).count()
        return higher_xp_count + 1

    @classmethod
    def get_user_reading_passport(cls, user_id) -> Optional[Dict[str, Any]]:
        """
        Kitobxon pasporti uchun barcha tahliliy ma'lumotlarni yig'uvchi markaziy selektor.
        """
        _verify_postgres()
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return None

        # O(1) va production-safe yondashuv: UserReadingStatistic dan to'g'ridan-to'g'ri olamiz
        stats, _ = UserReadingStatistic.objects.get_or_create(user=user)

        rank = cls.get_global_leaderboard_position(user_id=user.id)

        # Janr tahlili: FINISHED kitoblar ichidan eng ko'p o'qilgan TOP 1 ta janr (distinct=True)
        top_genre_obj = (
            Genre.objects.filter(
                books__library_items__user=user,
                books__library_items__status=LibraryItem.ReadingStatus.FINISHED,
            )
            .annotate(count=Count("books__library_items", distinct=True))
            .order_by("-count", "name")
            .first()
        )

        # Til tahlili: FINISHED kitoblar ichidan eng ko'p o'qilgan TOP 1 ta til (distinct=True)
        top_language_obj = (
            Language.objects.filter(
                books__library_items__user=user,
                books__library_items__status=LibraryItem.ReadingStatus.FINISHED,
            )
            .annotate(count=Count("books__library_items", distinct=True))
            .order_by("-count", "name")
            .first()
        )

        return {
            "okj_id": user.okj_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "total_xp": user.total_xp,
            "level": user.total_xp // 100,
            "rank": rank,
            "total_books_finished": stats.total_books_finished,
            "total_pages_read": stats.total_pages_read,
            "top_genre": top_genre_obj.name if top_genre_obj else None,
            "top_language": top_language_obj.name if top_language_obj else None,
        }

    @classmethod
    def get_global_leaderboard(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Umumiy platformadagi TOP eng faol kitobxonlar ro'yxati.
        [:limit] qat'iy cheklovi bilan qaytaradi.
        """
        _verify_postgres()
        users = (
            User.objects.filter(is_deleted=False, is_active=True)
            .order_by("-total_xp", "okj_number")[:limit]
        )

        results = []
        for idx, u in enumerate(users, start=1):
            results.append(
                {
                    "rank": idx,
                    "username": u.username,
                    "total_xp": u.total_xp,
                    "level": u.total_xp // 100,
                }
            )
        return results
