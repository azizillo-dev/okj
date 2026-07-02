import pytest
from unittest.mock import patch
from django.db import OperationalError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from books.models import Book, Author
from accounts.models import User
from posts.models import Post
from search.selectors import SearchSelector, _verify_postgres


@pytest.mark.django_db
class TestSearchInfrastructure:
    def test_sqlite_prohibition_raises_operational_error(self):
        """Agar vendor sqlite bo'lib qolsa, OperationalError ko'tarilishi shart."""
        with patch("search.selectors.connections") as mock_conns:
            mock_conns["default"].vendor = "sqlite"
            with pytest.raises(OperationalError, match="Bu modul faqat PostgreSQL'da ishlaydi"):
                _verify_postgres()

    def test_verify_postgres_passes_on_real_postgres(self):
        """Real PostgreSQL'da _verify_postgres hech qanday xatosiz ishlaydi."""
        _verify_postgres()


@pytest.mark.django_db
class TestSearchSelectors:
    def test_book_search_vector_auto_update_and_fts(self):
        author = Author.objects.create(name="Abdulla Qodiriy", slug="abdulla-qodiriy")
        book = Book.objects.create(
            title="O'tkan kunlar",
            slug="otkan-kunlar",
            verification_status=Book.VerificationStatus.VERIFIED,
        )
        book.authors.add(author)

        # Signal search_vector ni yangilaganini tekshiramiz
        book.refresh_from_db()
        assert book.search_vector is not None

        # FTS va Trigram qidiruvi (imlo xatosi bilan: "Otkan kunlar" yoki "Qodiriy")
        results = SearchSelector.search_books("Otkan kunlar")
        assert book in list(results)

        results_by_author = SearchSelector.search_books("Qodiriy")
        assert book in list(results_by_author)

    def test_user_search_trigram(self):
        user = User.objects.create_user(
            username="navoiy_lover",
            first_name="Alisher",
            last_name="Kitobxon",
            password="testpassword123",
            okj_number=8881,
        )

        results = SearchSelector.search_users("navoyi")
        assert user in list(results)

    def test_post_search_trigram(self):
        user = User.objects.create_user(
            username="reviewer",
            password="testpassword123",
            okj_number=8882,
        )
        post = Post.objects.create(
            user=user,
            post_type=Post.PostType.REVIEW,
            title="Ajoyib asar taqrizi",
            content="Juda chuqur falsafiy ma'noga ega kitob ekan",
            visibility=Post.Visibility.PUBLIC,
            moderation_status=Post.ModerationStatus.APPROVED,
            status=Post.Status.PUBLISHED,
        )

        results = SearchSelector.search_posts("falsafiy")
        assert post in list(results)

    def test_global_search_all(self):
        user = User.objects.create_user(username="qodiriy_fan", password="pwd", okj_number=8883)
        author = Author.objects.create(name="Abdulla Qodiriy", slug="abdulla-qodiriy-2")
        book = Book.objects.create(title="Mehrobdan chayon", slug="mehrobdan-chayon", verification_status=Book.VerificationStatus.VERIFIED)
        book.authors.add(author)

        results = SearchSelector.global_search("Qodiriy", search_type="ALL")
        assert len(results["books"]) >= 1


@pytest.mark.django_db
class TestSearchApi:
    def test_global_search_api_endpoint(self):
        client = APIClient()
        Book.objects.create(title="Yulduzli tunlar", slug="yulduzli-tunlar", verification_status=Book.VerificationStatus.VERIFIED)

        response = client.get(reverse("search:global-search"), {"q": "Yulduzli", "type": "BOOKS"})
        assert response.status_code == status.HTTP_200_OK
        assert "books" in response.data
        assert len(response.data["books"]) >= 1
        assert response.data["books"][0]["title"] == "Yulduzli tunlar"
