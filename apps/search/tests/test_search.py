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
from search.serializers import BookSearchResultSerializer, UserSearchResultSerializer, PostSearchResultSerializer


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
class TestSearchSerializers:
    def test_user_serializer_level_calculation(self):
        user = User.objects.create_user(
            username="xp_master",
            first_name="Anvar",
            last_name="Karimov",
            password="testpassword123",
            okj_number=9001,
        )
        user.total_xp = 750
        user.save()

        serializer = UserSearchResultSerializer(user)
        assert serializer.data["level"] == 7  # 750 // 100 = 7

    def test_post_serializer_text_formatting(self):
        user = User.objects.create_user(username="quote_user", password="pwd", okj_number=9002)
        quote_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Har bir inson kitob o'qishi kerak. Bu juda uzoq iqtibos matni..." * 10,
            visibility=Post.Visibility.PUBLIC,
            moderation_status=Post.ModerationStatus.APPROVED,
            status=Post.Status.PUBLISHED,
        )
        serializer = PostSearchResultSerializer(quote_post)
        assert len(serializer.data["text"]) <= 150
        assert serializer.data["user"] == "quote_user"


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

        book.refresh_from_db()
        assert book.search_vector is not None

        results = SearchSelector.search_books("Otkan kunlar")
        assert book in list(results)

        results_by_author = SearchSelector.search_books("Qodiriy")
        assert book in list(results_by_author)

    def test_search_books_by_isbn(self):
        """ISBN bo'yicha qidiruv (tire va bo'shliqlarsiz yoki formatli)."""
        book = Book.objects.create(
            title="Nodir kitob",
            slug="nodir-kitob",
            isbn_13="9789943012345",
            verification_status=Book.VerificationStatus.VERIFIED,
        )
        results = list(SearchSelector.search_books("978-9943-01-234-5"))
        assert book in results

    def test_search_books_duplicate_prevention(self):
        """2 va undan ortiq mualliflik kitob qidiruv natijasida FAQAT BITTA marta chiqishini tasdiqlash."""
        author1 = Author.objects.create(name="Abdulla Qodiriy", slug="abdulla-qodiriy-dup")
        author2 = Author.objects.create(name="Cho'lpon", slug="cholpon-dup")
        book = Book.objects.create(
            title="O'zbek adabiyoti antologiyasi",
            slug="ozbek-adabiyoti-antologiyasi",
            verification_status=Book.VerificationStatus.VERIFIED,
        )
        book.authors.add(author1, author2)

        results = list(SearchSelector.search_books("adabiyoti"))
        matching_books = [b for b in results if b.id == book.id]
        assert len(matching_books) == 1

    def test_search_books_n_plus_one_prevention(self, django_assert_num_queries):
        """prefetch_related('authors') orqali N+1 muammosi bo'lmasligini va O(1) query countni isbotlash."""
        author1 = Author.objects.create(name="Alisher Navoiy", slug="alisher-navoiy-n1")
        for i in range(2):
            b = Book.objects.create(
                title=f"Xamsa jild {i}",
                slug=f"xamsa-jild-{i}",
                verification_status=Book.VerificationStatus.VERIFIED,
            )
            b.authors.add(author1)

        # 2 ta kitob uchun SQL so'rovlar soni o'lchanadi (1 ta kitoblar, 1 ta prefetch mualliflar = 2 query)
        with django_assert_num_queries(2):
            qs2 = list(SearchSelector.search_books("Xamsa"))
            data2 = BookSearchResultSerializer(qs2, many=True).data
            assert len(data2) >= 2
            for item in data2:
                assert len(item["authors"]) >= 1

        # Natijalar sonini 10 barobar ko'paytiramiz (yana 10 ta kitob va 10 ta muallif qo'shildi)
        for i in range(2, 12):
            author = Author.objects.create(name=f"Muallif N1 {i}", slug=f"muallif-n1-{i}")
            b = Book.objects.create(
                title=f"Xamsa jild {i}",
                slug=f"xamsa-jild-{i}",
                verification_status=Book.VerificationStatus.VERIFIED,
            )
            b.authors.add(author)

        # 12 ta kitob va ko'plab mualliflar bo'lganda ham SQL so'rov soni aniq 2 ta qolishi shart (O(1))!
        with django_assert_num_queries(2):
            qs12 = list(SearchSelector.search_books("Xamsa"))
            data12 = BookSearchResultSerializer(qs12, many=True).data
            assert len(data12) >= 12
            for item in data12:
                assert len(item["authors"]) >= 1

    def test_user_search_trigram(self):
        user = User.objects.create_user(
            username="navoiy_lover",
            first_name="Alisher",
            last_name="Kitobxon",
            password="testpassword123",
            okj_number=9003,
        )
        results = SearchSelector.search_users("navoyi")
        assert user in list(results)

    def test_post_search_trigram(self):
        user = User.objects.create_user(username="reviewer_n", password="pwd", okj_number=9004)
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


@pytest.mark.django_db
class TestSearchApi:
    def test_global_search_api_endpoint(self):
        client = APIClient()
        Book.objects.create(title="Yulduzli tunlar", slug="yulduzli-tunlar", verification_status=Book.VerificationStatus.VERIFIED)

        response = client.get(reverse("search:global-search"), {"q": "Yulduzli", "type": "BOOKS"})
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "results" in response.data["data"]
        assert len(response.data["data"]["results"]) >= 1
        assert response.data["data"]["results"][0]["title"] == "Yulduzli tunlar"

    def test_search_api_pagination(self):
        client = APIClient()
        for i in range(25):
            Book.objects.create(
                title=f"Paginatsiya kitobi {i}",
                slug=f"paginatsiya-kitobi-{i}",
                verification_status=Book.VerificationStatus.VERIFIED,
            )
        response = client.get(reverse("search:global-search"), {"q": "Paginatsiya", "type": "BOOKS", "page": 1, "page_size": 10})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] >= 25
        assert len(response.data["data"]["results"]) == 10
