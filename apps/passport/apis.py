"""
OKJ PLATFORM - PASSPORT APIS (apps/passport/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha API ko'rinishlari (Views)
maksimal darajada yupqa (Thin Views) bo'lib, mantiqni selektorlarga topshirishi shart.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .selectors import PassportSelector
from .serializers import ReadingPassportSerializer, LeaderboardItemSerializer


class UserReadingPassportApi(APIView):
    """
    Kitobxonning shaxsiy elektron pasporti yoki ommaviy pasport:
    GET /api/v1/passport/?okj_id=OKJ-10492 (yoki autentifikatsiya orqali)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from accounts.models import User
        okj_id = request.query_params.get("okj_id")
        user = None

        if okj_id and okj_id != "me":
            user = User.objects.filter(okj_id__iexact=okj_id, is_deleted=False).first()
            if not user:
                user = User.objects.filter(username__iexact=okj_id, is_deleted=False).first()

        if not user and request.user.is_authenticated:
            user = request.user

        if not user:
            user = User.objects.filter(is_deleted=False).first()

        if not user:
            return Response({"success": False, "detail": "Kitobxon pasporti topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        passport_data = PassportSelector.get_user_reading_passport(user_id=user.id)
        if not passport_data:
            return Response({"success": False, "detail": "Kitobxon pasporti topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReadingPassportSerializer(passport_data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class GlobalLeaderboardApi(APIView):
    """
    Umumiy platformadagi TOP 50 ta eng faol kitobxonlar ro'yxati:
    GET /api/v1/passport/leaderboard/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        leaderboard_data = PassportSelector.get_global_leaderboard(limit=50)
        serializer = LeaderboardItemSerializer(leaderboard_data, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
