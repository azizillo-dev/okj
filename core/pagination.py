"""
OKJ PLATFORM - PAGINATION CLASSES (core/pagination.py)
Nega bu fayl kerak: Barcha ro'yxat (list) javoblarida `count`, `next`, `previous`, va `results`
bir xil o'lchamda qaytishi hamda mobil ilovada cheksiz surish (infinite scroll) oson ishlashi uchun.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Standart sahifalash: 1 ta sahifada 20 ta yozuv (m-n: lenta yoki kitoblar qidiruvi)."""
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "data": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )


class LargeResultsSetPagination(StandardResultsSetPagination):
    """Kengaytirilgan sahifalash: 1 ta sahifada 50 ta yozuv (m-n: viloyat/tumanlar ro'yxati)."""
    page_size = 50
    max_page_size = 200
