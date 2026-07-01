"""
OKJ PLATFORM - ACCOUNTS API VIEWS (apps/accounts/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha bu yerdagi viewlar (apis.py)
JUDE YENGIL (Thin Views) bo'ladi. Ular faqat JSON payloadni serializer orqali olib,
to'g'ridan-to'g'ri `services.py` yoki `selectors.py` ga yuboradi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from core.responses import APIResponse
from .selectors import UserSelector, DistrictSelector
from .services import UserService
from .serializers import (
    DistrictSerializer,
    ReaderProfileReadSerializer,
    ReaderRegisterSerializer,
    ReaderProfileUpdateSerializer,
)


class DistrictListApi(APIView):
    """Viloyat va Tumanlar ro'yxatini olish API."""
    permission_classes = [AllowAny]

    def get(self, request):
        region = request.query_params.get("region")
        if region:
            districts = DistrictSelector.get_districts_by_region(region)
        else:
            districts = DistrictSelector.get_all_districts()

        serializer = DistrictSerializer(districts, many=True)
        return APIResponse(data=serializer.data, message="Tumanlar ro'yxati yuklandi.")


class ReaderRegisterApi(APIView):
    """Yangi kitobxon ro'yxatdan o'tkazish API."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReaderRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.register_reader(**serializer.validated_data)
        read_serializer = ReaderProfileReadSerializer(user)
        return APIResponse(
            data=read_serializer.data,
            message=f"Tabriklar! Sizga {user.okj_id} pasport raqami berildi.",
            status_code=status.HTTP_201_CREATED,
        )


class ReaderProfileApi(APIView):
    """Joriy kitobxon profilini ko'rish va tahrirlash API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserSelector.get_user_by_id(request.user.id)
        serializer = ReaderProfileReadSerializer(user)
        return APIResponse(data=serializer.data, message="Profil ma'lumotlari.")

    def patch(self, request):
        serializer = ReaderProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_user = UserService.update_profile(user=request.user, **serializer.validated_data)
        read_serializer = ReaderProfileReadSerializer(updated_user)
        return APIResponse(data=read_serializer.data, message="Profil muvaffaqiyatli yangilandi.")


class DistrictLeaderboardApi(APIView):
    """Tuman bo'yicha eng yuqori XP ga ega kitobxonlar reytingi API."""
    permission_classes = [AllowAny]

    def get(self, request, district_id: int):
        readers = UserSelector.get_district_leaderboard(district_id=district_id)
        serializer = ReaderProfileReadSerializer(readers, many=True)
        return APIResponse(data=serializer.data, message="Tuman reytingi yuklandi.")
