"""
OKJ PLATFORM - SEARCH SELECTORS (apps/search/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha barcha o'qish (Read/Search)
so'rovlari va PostgreSQL Trigram + FTS mantiqlari selektorlarda joylashishi shart.
"""

from typing import Optional, Dict, Any
from django.db import connections, OperationalError
from django.db.models import Q, F, FloatField, Subquery, OuterRef
from django.db.models.functions import Coalesce, Greatest
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from books.models import Book, Author
from accounts.models import User
from posts.models import Post


def _verify_postgres():
    """
    Twelve-Factor & Infrastructure qoidasi:
    Bu modul faqat PostgreSQL'da ishlaydi. Agar testlar yoki lokal muhit
    SQLite'ga tushib qolsa, OperationalError qaytaramiz.
    """
    if connections["default"].vendor != "postgresql":
        raise OperationalError(
            "Bu modul faqat PostgreSQL'da ishlaydi. SQLite ruxsat etilmaydi. "
            "Real Trigram va FTS imlo xatolarini tuzatish mantiqlari faqat real Postgres ustida ishlaydi."
        )


class SearchSelector:
    """Universal Global Search selektori."""

    @classmethod
    def global_search(cls, query_string: str, search_type: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Universal qidiruv selektori.
        search_type: BOOKS, USERS, POSTS, ALL
        """
        _verify_postgres()
        search_type = (search_type or "ALL").upper().strip()

        results = {
            "query": query_string,
            "books": Book.objects.none(),
            "users": User.objects.none(),
            "posts": Post.objects.none(),
        }

        if not query_string or not query_string.strip():
            return results

        query_string = query_string.strip()

        if search_type in ["BOOKS", "ALL"]:
            results["books"] = cls.search_books(query_string, limit=limit)
        if search_type in ["USERS", "ALL"]:
            results["users"] = cls.search_users(query_string, limit=limit)
        if search_type in ["POSTS", "ALL"]:
            results["posts"] = cls.search_posts(query_string, limit=limit)

        return results

    @classmethod
    def search_books(cls, query_string: str, limit: Optional[int] = None):
        """
        Book Search:
        (a) ISBN qidiruv: isbn_10 yoki isbn_13 bo'yicha qat'iy va tezkor moslik.
        (b) Author & Title Fuzzy Matching: TrigramSimilarity title va authors__name ustida hisoblanib, Greatest() bilan saralanadi.
            Subquery orqali annotatsiya qilinib, dublikat (bitta kitob bir necha marta chiqishi) 100% oldi olingan.
        (c) prefetch_related("authors") orqali N+1 muammosi 100% bartaraf etiladi.
        """
        _verify_postgres()
        if not query_string or not query_string.strip():
            return Book.objects.none()

        query_string = query_string.strip()
        search_query = SearchQuery(query_string)

        clean_isbn = query_string.replace("-", "").replace(" ", "").strip()
        isbn_q = Q()
        if any(char.isdigit() for char in clean_isbn) and len(clean_isbn) in [10, 13]:
            isbn_q = Q(isbn_10=clean_isbn) | Q(isbn_13=clean_isbn) | Q(isbn_10=query_string) | Q(isbn_13=query_string)

        author_sim_subquery = Subquery(
            Author.objects.filter(books=OuterRef("pk"), is_deleted=False)
            .annotate(sim=TrigramSimilarity("name", query_string))
            .order_by("-sim")
            .values("sim")[:1],
            output_field=FloatField(),
        )

        qs = Book.objects.filter(is_deleted=False, verification_status=Book.VerificationStatus.VERIFIED)

        qs = qs.annotate(
            fts_rank=SearchRank(F("search_vector"), search_query),
            title_sim=TrigramSimilarity("title", query_string),
            author_sim=Coalesce(author_sim_subquery, 0.0, output_field=FloatField()),
        ).annotate(
            similarity_score=Greatest(
                Coalesce(F("fts_rank"), 0.0, output_field=FloatField()),
                Coalesce(F("title_sim"), 0.0, output_field=FloatField()),
                F("author_sim"),
                output_field=FloatField(),
            )
        )

        filter_q = (
            Q(search_vector=search_query)
            | Q(title_sim__gte=0.25)
            | Q(author_sim__gte=0.25)
            | Q(title__icontains=query_string)
        )
        if isbn_q:
            filter_q = filter_q | isbn_q

        qs = qs.filter(filter_q).prefetch_related("authors").order_by("-similarity_score", "-average_rating")

        if limit is not None:
            qs = qs[:limit]
        return qs

    @classmethod
    def search_users(cls, query_string: str, limit: Optional[int] = None):
        """
        User Search: Username ustidan trigram va unaccent moslikni qaytaradi.
        """
        _verify_postgres()
        if not query_string or not query_string.strip():
            return User.objects.none()

        query_string = query_string.strip()
        qs = User.objects.filter(is_deleted=False, is_active=True).annotate(
            similarity_score=TrigramSimilarity("username", query_string)
        ).filter(
            Q(similarity_score__gte=0.25)
            | Q(username__icontains=query_string)
            | Q(username__unaccent__icontains=query_string)
            | Q(first_name__icontains=query_string)
            | Q(last_name__icontains=query_string)
        ).order_by("-similarity_score", "username")

        if limit is not None:
            qs = qs[:limit]
        return qs

    @classmethod
    def search_posts(cls, query_string: str, limit: Optional[int] = None):
        """
        Post Search: Reviews (taqriz) va Quotes (iqtibos) ichidan trigram-similarity qidiruvi.
        select_related("user") orqali N+1 muammosi bartaraf etiladi.
        """
        _verify_postgres()
        if not query_string or not query_string.strip():
            return Post.objects.none()

        query_string = query_string.strip()
        qs = Post.published_objects.filter(
            post_type__in=[Post.PostType.REVIEW, Post.PostType.QUOTE],
            visibility=Post.Visibility.PUBLIC,
            moderation_status=Post.ModerationStatus.APPROVED,
        ).select_related("user").annotate(
            sim_title=TrigramSimilarity("title", query_string),
            sim_content=TrigramSimilarity("content", query_string),
            sim_quote=TrigramSimilarity("quote_text", query_string),
        ).annotate(
            similarity_score=Greatest(
                Coalesce(F("sim_title"), 0.0, output_field=FloatField()),
                Coalesce(F("sim_content"), 0.0, output_field=FloatField()),
                Coalesce(F("sim_quote"), 0.0, output_field=FloatField()),
                output_field=FloatField(),
            )
        ).filter(
            Q(similarity_score__gte=0.2)
            | Q(title__icontains=query_string)
            | Q(content__icontains=query_string)
            | Q(quote_text__icontains=query_string)
        ).order_by("-similarity_score", "-published_at")

        if limit is not None:
            qs = qs[:limit]
        return qs
