"""
OKJ PLATFORM - FEED RANKING APIS (apps/feed_ranking/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha yengil (Thin Views).
Hech qanday ORM yoki kesh mantiqi bo'lmaydi, faqat selektorlar chaqiriladi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from posts.serializers import PostReadSerializer
from feed_ranking.selectors import FeedRankingSelector


class UserRankedFeedApi(APIView):
    """
    Algoritmik saralangan shaxsiy ijtimoiy lenta (Home Feed) API.
    Faqat autentifikatsiyadan o'tgan kitobxonlar uchun.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
        except (ValueError, TypeError):
            page = 1
        try:
            page_size = int(request.query_params.get("page_size", 20))
        except (ValueError, TypeError):
            page_size = 20

        posts = FeedRankingSelector.get_ranked_feed_for_user(
            user=request.user, page=page, page_size=page_size
        )
        total_count = FeedRankingSelector.get_total_feed_count(user=request.user)

        serializer = PostReadSerializer(posts, many=True, context={"request": request})

        next_link = None
        if page * page_size < total_count:
            next_link = f"/api/v1/posts/feed/?page={page + 1}&page_size={page_size}"

        previous_link = None
        if page > 1:
            previous_link = f"/api/v1/posts/feed/?page={page - 1}&page_size={page_size}"

        return Response(
            {
                "success": True,
                "data": {
                    "count": total_count,
                    "next": next_link,
                    "previous": previous_link,
                    "results": serializer.data,
                },
            }
        )
