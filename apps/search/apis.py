"""
OKJ PLATFORM - SEARCH APIS (apps/search/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha API ko'rinishlari (Views)
maksimal darajada yupqa (Thin Views) bo'lib, mantiqni selektorlarga topshirishi shart.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .selectors import SearchSelector


class GlobalSearchApi(APIView):
    """
    Global universal qidiruv endpointi:
    GET /api/v1/search/?q={query_string}&type={BOOKS/USERS/POSTS/ALL}
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query_string = request.query_params.get("q", "").strip()
        search_type = request.query_params.get("type", "ALL").upper().strip()

        results = SearchSelector.global_search(query_string=query_string, search_type=search_type)

        formatted_books = [
            {
                "id": str(b.id),
                "title": b.title,
                "slug": b.slug,
                "average_rating": float(b.average_rating),
            }
            for b in results.get("books", [])
        ]

        formatted_users = [
            {
                "id": str(u.id),
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
            }
            for u in results.get("users", [])
        ]

        formatted_posts = [
            {
                "id": str(p.id),
                "post_type": p.post_type,
                "title": p.title,
                "content_snippet": (p.content[:150] if p.content else p.quote_text[:150]),
            }
            for p in results.get("posts", [])
        ]

        data = {
            "query": query_string,
            "type": search_type,
            "books": formatted_books,
            "users": formatted_users,
            "posts": formatted_posts,
        }
        return Response(data, status=status.HTTP_200_OK)
