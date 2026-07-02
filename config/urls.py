"""
OKJ PLATFORM - ROOT URL CONFIGURATION
Nega kerak: Barcha API marshrutlarini /api/v1/ prefigi ostida toza birlashtirish
hamda Swagger/OpenAPI hujjatlash tizimini taqdim etish.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from core.admin_dashboard import AdminDashboardView


def health_check(request):
    """Konteynerlar salomatligini tekshirish uchun yengil endpoint (<1ms)."""
    return JsonResponse({"status": "healthy", "platform": "OKJ Enterprise Modular Monolith"}, status=200)


urlpatterns = [
    # Health check & Monitoring
    path("health/", health_check, name="health_check"),

    # Django Admin Panel & Operational Dashboard
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/", admin.site.urls),

    # OpenAPI 3.0 & Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # V1 API Endpoints
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/books/", include("books.urls")),
    path("api/v1/library/", include("library.urls")),
    path("api/v1/posts/feed/", include("feed_ranking.urls")),
    path("api/v1/posts/", include("posts.urls")),
    path("api/v1/posts/", include("interactions.urls")),
    path("api/v1/", include("comments.urls")),
    path("api/v1/users/", include("follows.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/search/", include("search.urls")),
    path("api/v1/passport/", include("passport.urls")),
    path("api/v1/moderation/", include("moderation.urls")),
]
