"""
OKJ PLATFORM - SEARCH APIS (apps/search/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha API ko'rinishlari (Views)
maksimal darajada yupqa (Thin Views) bo'lib, mantiqni selektorlarga topshirishi,
hamda transport qatlami uchun serializer va paginatsiyani qo'llashi shart.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from core.pagination import StandardResultsSetPagination
from .selectors import SearchSelector
from .serializers import (
    BookSearchResultSerializer,
    UserSearchResultSerializer,
    PostSearchResultSerializer,
)


class GlobalSearchApi(APIView):
    """
    Global universal va paginatsiyalangan qidiruv endpointi:
    GET /api/v1/search/?q={query_string}&type={BOOKS/USERS/POSTS/ALL}&page={page}&page_size={page_size}
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        query_string = request.query_params.get("q", "").strip()
        search_type = request.query_params.get("type", "ALL").upper().strip()

        if search_type == "BOOKS":
            qs = SearchSelector.search_books(query_string)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qs, request, view=self)
            serializer = BookSearchResultSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        if search_type == "USERS":
            qs = SearchSelector.search_users(query_string)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qs, request, view=self)
            serializer = UserSearchResultSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        if search_type == "POSTS":
            qs = SearchSelector.search_posts(query_string)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qs, request, view=self)
            serializer = PostSearchResultSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # ALL turi uchun
        paginator = self.pagination_class()
        try:
            page_size = int(request.query_params.get(paginator.page_size_query_param, paginator.page_size))
        except (ValueError, TypeError):
            page_size = paginator.page_size
        page_size = min(max(page_size, 1), paginator.max_page_size)

        results = SearchSelector.global_search(query_string=query_string, search_type="ALL", limit=page_size)

        data = {
            "query": query_string,
            "type": search_type,
            "books": BookSearchResultSerializer(results["books"], many=True).data,
            "users": UserSearchResultSerializer(results["users"], many=True).data,
            "posts": PostSearchResultSerializer(results["posts"], many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)
