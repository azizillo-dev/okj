"""
OKJ PLATFORM - SEARCH SELECTORS (apps/search/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha barcha o'qish (Read/Search)
so'rovlari va PostgreSQL Trigram + FTS mantiqlari selektorlarda joylashishi shart.
"""

from typing import Optional, Dict, Any, List
from django.db import connections, OperationalError
from django.db.models import Q, F, FloatField
from django.db.models.functions import Coalesce, Greatest
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from books.models import Book
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
    def global_search(cls, query_string: str, search_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Universal, paginatsiyalangan yoki limitlangan qidiruv.
        search_type: BOOKS, USERS, POSTS, ALL
        """
        _verify_postgres()
        search_type = (search_type or "ALL").upper().strip()

        results = {
            "query": query_string,
            "books": [],
            "users": [],
            "posts": [],
        }

        if not query_string or not query_string.strip():
            return results

        query_string = query_string.strip()

        if search_type in ["BOOKS", "ALL"]:
            results["books"] = list(cls.search_books(query_string))
        if search_type in ["USERS", "ALL"]:
            results["users"] = list(cls.search_users(query_string))
        if search_type in ["POSTS", "ALL"]:
            results["posts"] = list(cls.search_posts(query_string))

        return results

    @classmethod
    def search_books(cls, query_string: str, limit: int = 20):
        """
        Book Search: search_vector va TrigramSimilarity orqali Full-Text Search.
        Imlo xatolari bilan yozilganda ham (masalan "Otkan kunlar") 0.3 dan yuqori
        o'xshashlikdagi kitoblarni topadi.
        """
        _verify_postgres()
        if not query_string or not query_string.strip():
            return Book.objects.none()

        query_string = query_string.strip()
        search_query = SearchQuery(query_string)

        qs = Book.objects.filter(is_deleted=False, verification_status=Book.VerificationStatus.VERIFIED)
        
        qs = qs.annotate(
            fts_rank=SearchRank(F("search_vector"), search_query),
            trigram_sim=TrigramSimilarity("title", query_string),
        ).annotate(
            combined_score=Greatest(
                Coalesce(F("fts_rank"), 0.0, output_field=FloatField()),
                Coalesce(F("trigram_sim"), 0.0, output_field=FloatField()),
                output_field=FloatField(),
            )
        ).filter(
            Q(search_vector=search_query) | Q(trigram_sim__gte=0.25) | Q(title__icontains=query_string)
        ).order_by("-combined_score", "-average_rating")[:limit]

        return qs

    @classmethod
    def search_users(cls, query_string: str, limit: int = 20):
        """
        User Search: Username ustidan trigram va unaccent moslikni qaytaradi.
        """
        _verify_postgres()
        if not query_string or not query_string.strip():
            return User.objects.none()

        query_string = query_string.strip()
        qs = User.objects.filter(is_deleted=False, is_active=True).annotate(
            similarity=TrigramSimilarity("username", query_string)
        ).filter(
            Q(similarity__gte=0.25)
            | Q(username__icontains=query_string)
            | Q(username__unaccent__icontains=query_string)
            | Q(first_name__icontains=query_string)
            | Q(last_name__icontains=query_string)
        ).order_by("-similarity", "username")[:limit]

        return qs

    @classmethod
    def search_posts(cls, query_string: str, limit: int = 20):
        """
        Post Search: Reviews (taqriz) va Quotes (iqtibos) ichidan trigram-similarity qidiruvi.
        """
        _verify_postgres()
        if not query_string or not query_string.strip():
            return Post.objects.none()

        query_string = query_string.strip()
        qs = Post.published_objects.filter(
            post_type__in=[Post.PostType.REVIEW, Post.PostType.QUOTE],
            visibility=Post.Visibility.PUBLIC,
            moderation_status=Post.ModerationStatus.APPROVED,
        ).annotate(
            sim_title=TrigramSimilarity("title", query_string),
            sim_content=TrigramSimilarity("content", query_string),
            sim_quote=TrigramSimilarity("quote_text", query_string),
        ).annotate(
            max_sim=Greatest(
                Coalesce(F("sim_title"), 0.0, output_field=FloatField()),
                Coalesce(F("sim_content"), 0.0, output_field=FloatField()),
                Coalesce(F("sim_quote"), 0.0, output_field=FloatField()),
                output_field=FloatField(),
            )
        ).filter(
            Q(max_sim__gte=0.2)
            | Q(title__icontains=query_string)
            | Q(content__icontains=query_string)
            | Q(quote_text__icontains=query_string)
        ).order_by("-max_sim", "-published_at")[:limit]

        return qs
