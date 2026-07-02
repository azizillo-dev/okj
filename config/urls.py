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


from django.db import connection
from django.core.cache import cache


def health_check(request):
    """Konteynerlar salomatligini (Database va Redis ulanishini) tekshirish uchun endpoint."""
    db_status = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_status = "unreachable"

    redis_status = "ok"
    try:
        if hasattr(cache, "client") and hasattr(cache.client, "get_client"):
            cache.client.get_client().ping()
        else:
            cache.set("health_check_ping", "pong", 5)
            if cache.get("health_check_ping") != "pong":
                redis_status = "unreachable"
    except Exception:
        redis_status = "unreachable"

    is_healthy = (db_status == "ok" and redis_status == "ok")
    status_code = 200 if is_healthy else 503
    status_str = "healthy" if is_healthy else "unhealthy"

    return JsonResponse(
        {
            "status": status_str,
            "platform": "OKJ Enterprise Modular Monolith",
            "database": db_status,
            "redis": redis_status,
        },
        status=status_code,
    )


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
