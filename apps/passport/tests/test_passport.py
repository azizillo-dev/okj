import pytest
from unittest.mock import patch
from django.db import OperationalError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from books.models import Book, Author, Genre, Language
from library.models import LibraryItem, UserReadingStatistic
from passport.selectors import PassportSelector, _verify_postgres


@pytest.mark.django_db
class TestPassportInfrastructure:
    def test_sqlite_prohibition_raises_operational_error(self):
        """Agar vendor sqlite bo'lib qolsa, OperationalError ko'tarilishi shart."""
        with patch("passport.selectors.connections") as mock_conns:
            mock_conns["default"].vendor = "sqlite"
            with pytest.raises(OperationalError, match="Bu modul faqat PostgreSQL'da ishlaydi"):
                _verify_postgres()


@pytest.mark.django_db
class TestPassportAnalytics:
    def test_leaderboard_ordering_and_rank_calculation(self):
        u1 = User.objects.create_user(username="user_low", password="pwd", okj_number=9101, okj_id="OKJ-9101", total_xp=100)
        u2 = User.objects.create_user(username="user_mid", password="pwd", okj_number=9102, okj_id="OKJ-9102", total_xp=500)
        u3 = User.objects.create_user(username="user_high", password="pwd", okj_number=9103, okj_id="OKJ-9103", total_xp=1200)

        # Leaderboard tartibi
        leaderboard = PassportSelector.get_global_leaderboard(limit=10)
        assert len(leaderboard) >= 3
        usernames_in_order = [item["username"] for item in leaderboard]
        assert usernames_in_order.index("user_high") < usernames_in_order.index("user_mid")
        assert usernames_in_order.index("user_mid") < usernames_in_order.index("user_low")

        # Shaxsiy rank hisobi (.count() + 1)
        rank_u3 = PassportSelector.get_global_leaderboard_position(user_id=u3.id)
        rank_u2 = PassportSelector.get_global_leaderboard_position(user_id=u2.id)
        assert rank_u3 < rank_u2

    def test_user_reading_passport_stats_from_cache(self):
        user = User.objects.create_user(username="passport_user", password="pwd", okj_number=9104, okj_id="OKJ-9104", total_xp=850)
        stats, _ = UserReadingStatistic.objects.get_or_create(user=user)
        stats.total_books_finished = 15
        stats.total_pages_read = 3400
        stats.save()

        passport = PassportSelector.get_user_reading_passport(user_id=user.id)
        assert passport["total_books_finished"] == 15
        assert passport["total_pages_read"] == 3400
        assert passport["level"] == 8  # 850 // 100

    def test_top_genre_and_language_distinct_calculation(self):
        user = User.objects.create_user(username="genre_fan", password="pwd", okj_number=9105, okj_id="OKJ-9105")
        author1 = Author.objects.create(name="Muallif 1", slug="muallif-1-pass")
        author2 = Author.objects.create(name="Muallif 2", slug="muallif-2-pass")

        genre_roman = Genre.objects.create(name="Tarixiy Roman", slug="tarixiy-roman")
        genre_sheir = Genre.objects.create(name="She'riyat", slug="sheiriyat")

        lang_uz = Language.objects.create(name="O'zbek", code="uz-pass")
        lang_en = Language.objects.create(name="Ingliz", code="en-pass")

        # 2 ta Tarixiy Roman kitob o'qildi (biri 2 ta muallifli, fan-out bo'lmasligi tekshiriladi)
        book1 = Book.objects.create(title="Roman 1", slug="roman-1-pass", language=lang_uz, verification_status=Book.VerificationStatus.VERIFIED)
        book1.authors.add(author1, author2)
        book1.genres.add(genre_roman)

        book2 = Book.objects.create(title="Roman 2", slug="roman-2-pass", language=lang_uz, verification_status=Book.VerificationStatus.VERIFIED)
        book2.authors.add(author1)
        book2.genres.add(genre_roman)

        # 1 ta She'riyat kitob o'qildi (ingliz tilida)
        book3 = Book.objects.create(title="Sheir 1", slug="sheir-1-pass", language=lang_en, verification_status=Book.VerificationStatus.VERIFIED)
        book3.authors.add(author1)
        book3.genres.add(genre_sheir)

        LibraryItem.objects.create(user=user, book=book1, status=LibraryItem.ReadingStatus.FINISHED)
        LibraryItem.objects.create(user=user, book=book2, status=LibraryItem.ReadingStatus.FINISHED)
        LibraryItem.objects.create(user=user, book=book3, status=LibraryItem.ReadingStatus.FINISHED)

        passport = PassportSelector.get_user_reading_passport(user_id=user.id)
        assert passport["top_genre"] == "Tarixiy Roman"
        assert passport["top_language"] == "O'zbek"


@pytest.mark.django_db
class TestPassportApis:
    def test_get_user_passport_unauthenticated_rejected(self):
        client = APIClient()
        response = client.get(reverse("passport:user-passport"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_passport_authenticated(self):
        user = User.objects.create_user(username="auth_passport", password="pwd", okj_number=9106, okj_id="OKJ-9106", total_xp=420)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(reverse("passport:user-passport"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["username"] == "auth_passport"
        assert response.data["data"]["level"] == 4

    def test_get_leaderboard_endpoint(self):
        client = APIClient()
        User.objects.create_user(username="top_leader", password="pwd", okj_number=9107, okj_id="OKJ-9107", total_xp=5000)

        response = client.get(reverse("passport:leaderboard"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) >= 1
        assert response.data["data"][0]["rank"] == 1
