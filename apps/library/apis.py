"""
OKJ PLATFORM - LIBRARY API VIEWS (apps/library/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Hech qanday ORM so'rovlari yozilmaydi, faqat `selectors.py` va `services.py` dan foydalanadi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.responses import APIResponse
from core.pagination import StandardResultsSetPagination
from .selectors import LibrarySelector
from .services import LibraryService
from .permissions import IsShelfOwner
from .serializers import (
    LibraryItemReadSerializer,
    AddShelfItemSerializer,
    UpdateShelfItemSerializer,
    LogReadingProgressSerializer,
    ReadingLogReadSerializer,
    UserReadingStatisticSerializer,
    ReadingGoalSerializer,
    CreateGoalSerializer,
)


class UserShelfListCreateApi(APIView):
    """Kitobxonning shaxsiy javonini olish va kitob qo'shish API."""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        status_filter = request.query_params.get("status")
        fav_param = request.query_params.get("is_favorite")
        is_favorite = True if fav_param == "true" else False if fav_param == "false" else None

        items = LibrarySelector.get_user_shelf(user_id=request.user.id, status=status_filter, is_favorite=is_favorite)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(items, request, view=self)
        serializer = LibraryItemReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AddShelfItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = LibraryService.add_to_shelf(user=request.user, **serializer.validated_data)
        read_serializer = LibraryItemReadSerializer(LibrarySelector.get_library_item(request.user.id, item.book_id))
        return APIResponse(
            data=read_serializer.data,
            message="Kitob kutubxonangizga qo'shildi.",
            status_code=status.HTTP_201_CREATED,
        )


class ShelfItemDetailApi(APIView):
    """Javondagi kitob holatini yangilash va o'chirish API."""
    permission_classes = [IsAuthenticated, IsShelfOwner]

    def patch(self, request, book_id: str):
        item = LibrarySelector.get_library_item(request.user.id, book_id)
        if not item:
            return APIResponse(message="Kitob javoningizdan topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = UpdateShelfItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_item = LibraryService.update_shelf_item(item=item, **serializer.validated_data)
        read_serializer = LibraryItemReadSerializer(updated_item)
        return APIResponse(data=read_serializer.data, message="Javon holati yangilandi.")

    def delete(self, request, book_id: str):
        item = LibrarySelector.get_library_item(request.user.id, book_id)
        if not item:
            return APIResponse(message="Kitob javoningizdan topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        LibraryService.remove_from_shelf(item)
        return APIResponse(message="Kitob javondan o'chirildi.", status_code=status.HTTP_200_OK)


class CurrentReadingApi(APIView):
    """Hozir o'qilayotgan kitoblar ro'yxati API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = LibrarySelector.get_current_reading(user_id=request.user.id)
        serializer = LibraryItemReadSerializer(items, many=True)
        return APIResponse(data=serializer.data)


class LogProgressApi(APIView):
    """Kunlik o'qilgan betlarni yozish va streak oshirish API."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogReadingProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = LibrarySelector._base_shelf_queryset().filter(
            id=serializer.validated_data["library_item_id"], user=request.user
        ).first()
        if not item:
            return APIResponse(message="Kutubxona yozuvi topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        log = LibraryService.log_reading_progress(
            user=request.user,
            library_item=item,
            pages_read=serializer.validated_data["pages_read"],
            minutes_spent=serializer.validated_data["minutes_spent"],
            note=serializer.validated_data.get("note", ""),
        )
        read_serializer = ReadingLogReadSerializer(log)
        return APIResponse(data=read_serializer.data, message="O'qish logi muvaffaqiyatli saqlandi va streak yangilandi.")


class ReadingStatisticsApi(APIView):
    """Umumiy o'qish statistikasi va olovcha API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = LibrarySelector.get_user_statistics(user_id=request.user.id)
        serializer = UserReadingStatisticSerializer(stats)
        return APIResponse(data=serializer.data)


class HeatmapApi(APIView):
    """Yillik o'qish xaritasi (Heatmap) API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year_param = request.query_params.get("year")
        year = int(year_param) if year_param and year_param.isdigit() else None
        data = LibrarySelector.get_reading_heatmap(user_id=request.user.id, year=year)
        return APIResponse(data=data)


class GoalsListCreateApi(APIView):
    """O'qish chaqiriqlari (Challenge / Goal) ro'yxati va yangisani yaratish API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = LibrarySelector.get_user_goals(user_id=request.user.id)
        serializer = ReadingGoalSerializer(goals, many=True)
        return APIResponse(data=serializer.data)

    def post(self, request):
        serializer = CreateGoalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        goal = LibraryService.create_or_update_goal(user=request.user, **serializer.validated_data)
        read_serializer = ReadingGoalSerializer(goal)
        return APIResponse(data=read_serializer.data, message="O'qish maqsadi muvaffaqiyatli saqlandi.")
