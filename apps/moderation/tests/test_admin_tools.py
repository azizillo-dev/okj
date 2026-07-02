import pytest
from django.urls import reverse
from django.test.client import RequestFactory
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.utils import CaptureQueriesContext
from django.db import connection
from accounts.models import User
from moderation.models import ContentReport, UserModerationFlag, AdminActionLog
from moderation.admin import ModerationQueueAdmin
from accounts.admin import UserAdmin
from posts.models import Post


def setup_admin_request(rf, user, post_data=None):
    request = rf.post("/", post_data) if post_data is not None else rf.post("/")
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


@pytest.mark.django_db
class TestAdminActionsAndAuditLogs:
    def test_ban_and_unban_users_action_creates_log_and_flag(self):
        admin_user = User.objects.createsuperuser(
            username="admin_action_test", password="pwd", okj_number=9001, okj_id="OKJ-9001"
        )
        target = User.objects.create_user(
            username="target_user_ban", password="pwd", okj_number=9002, okj_id="OKJ-9002"
        )

        rf = RequestFactory()
        request = setup_admin_request(rf, admin_user)

        user_admin = UserAdmin(User, admin.site)
        queryset = User.objects.filter(id=target.id)

        # 1. Ban action
        user_admin.ban_users(request, queryset)
        target.refresh_from_db()
        flag = UserModerationFlag.objects.get(user=target)
        assert flag.is_shadow_banned is True

        log = AdminActionLog.objects.filter(actor=admin_user, target_user=target, action_type="BAN").first()
        assert log is not None

        # 2. Unban action
        user_admin.unban_users(request, queryset)
        flag.refresh_from_db()
        assert flag.is_shadow_banned is False

        log_unban = AdminActionLog.objects.filter(actor=admin_user, target_user=target, action_type="UNBAN").first()
        assert log_unban is not None

    def test_grant_xp_action_adds_xp_and_logs(self):
        admin_user = User.objects.createsuperuser(
            username="admin_xp_test", password="pwd", okj_number=9003, okj_id="OKJ-9003"
        )
        target = User.objects.create_user(
            username="target_user_xp", password="pwd", okj_number=9004, okj_id="OKJ-9004", total_xp=50
        )

        rf = RequestFactory()
        request = setup_admin_request(rf, admin_user, {"apply": "1", "xp_amount": "150", "reason": "Bonuses"})

        user_admin = UserAdmin(User, admin.site)
        queryset = User.objects.filter(id=target.id)

        user_admin.grant_xp(request, queryset)
        target.refresh_from_db()
        assert target.total_xp == 200

        log_xp = AdminActionLog.objects.filter(actor=admin_user, target_user=target, action_type="GRANT_XP").first()
        assert log_xp is not None
        assert log_xp.metadata.get("amount") == 150

    def test_moderation_queue_actions(self):
        admin_user = User.objects.createsuperuser(
            username="admin_queue_test", password="pwd", okj_number=9005, okj_id="OKJ-9005"
        )
        author = User.objects.create_user(
            username="post_author_mod", password="pwd", okj_number=9006, okj_id="OKJ-9006"
        )
        post = Post.objects.create(user=author, post_type=Post.PostType.QUOTE, content="Bad Content")
        report = ContentReport.objects.create(
            reporter=author, content_type=ContentReport.ContentType.POST, target_id=post.id, reason=ContentReport.ReportReason.SPAM
        )

        rf = RequestFactory()
        request = setup_admin_request(rf, admin_user)

        queue_admin = ModerationQueueAdmin(ContentReport, admin.site)
        queryset = ContentReport.objects.filter(id=report.id)

        queue_admin.resolve_and_block(request, queryset)
        report.refresh_from_db()
        assert report.status == ContentReport.ReportStatus.RESOLVED

        post.refresh_from_db()
        assert post.is_deleted is True

        log_res = AdminActionLog.objects.filter(actor=admin_user, action_type="RESOLVE_REPORT").first()
        assert log_res is not None


@pytest.mark.django_db
class TestOperationalDashboardView:
    def test_admin_dashboard_view_query_count_and_access(self, client):
        admin_user = User.objects.createsuperuser(
            username="admin_dash_user", password="pwd", okj_number=9007, okj_id="OKJ-9007"
        )
        client.force_login(admin_user)

        url = reverse("admin-dashboard")

        # Test query count for stats fetching during view rendering
        with CaptureQueriesContext(connection) as ctx:
            response = client.get(url)

        assert response.status_code == 200
        assert "stats" in response.context
        stats = response.context["stats"]
        assert "total_users" in stats
        assert "today_users" in stats
        assert "pending_reports" in stats
        assert "shadow_banned_users" in stats
        assert "recent_posts" in stats

        # Verify that the dashboard view executed minimal queries
        assert len(ctx.captured_queries) <= 4
