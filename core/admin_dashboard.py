"""
OKJ PLATFORM - OPERATIONAL DASHBOARD (core/admin_dashboard.py)
Nega bu fayl kerak: Django admin bosh sahifasiga operatsion metrikalar
(5 ta kartochka) bitta optimallashgan query orqali chiqariladi.
"""

from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.utils import timezone


@method_decorator(staff_member_required, name="dispatch")
class AdminDashboardView(TemplateView):
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last_24h = now - timezone.timedelta(hours=24)

        # 5 ta kartochka uchun bitta optimallashgan SQL query
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM accounts_user WHERE is_deleted = false) as total_users,
                    (SELECT COUNT(*) FROM accounts_user WHERE is_deleted = false AND created_at >= %s) as today_users,
                    (SELECT COUNT(*) FROM moderation_contentreport WHERE status = 'PENDING') as pending_reports,
                    (SELECT COUNT(*) FROM moderation_usermoderationflag WHERE is_shadow_banned = true) as shadow_banned_users,
                    (SELECT COUNT(*) FROM posts_post WHERE is_deleted = false AND created_at >= %s) as recent_posts
            """, [today_start, last_24h])
            row = cursor.fetchone()

        context["stats"] = {
            "total_users": row[0] or 0,
            "today_users": row[1] or 0,
            "pending_reports": row[2] or 0,
            "shadow_banned_users": row[3] or 0,
            "recent_posts": row[4] or 0,
        }
        context["title"] = "OKJ Operatsion Dashboard"
        return context
