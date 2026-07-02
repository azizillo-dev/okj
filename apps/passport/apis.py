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
    Kitobxonning shaxsiy elektron pasporti:
    GET /api/v1/passport/ (Faqat Authenticated)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        passport_data = PassportSelector.get_user_reading_passport(user_id=request.user.id)
        if not passport_data:
            return Response({"detail": "Kitobxon pasporti topilmadi."}, status=status.HTTP_404_NOT_FOUND)

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
