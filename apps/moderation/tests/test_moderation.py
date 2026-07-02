import pytest
from unittest.mock import patch
from django.db import OperationalError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from posts.models import Post
from comments.models import Comment
from moderation.models import ContentReport, UserModerationFlag
from moderation.services import ModerationService
from moderation.selectors import ModerationSelector, _verify_postgres


@pytest.mark.django_db
class TestModerationInfrastructure:
    def test_sqlite_prohibition_raises_operational_error(self):
        """Agar vendor sqlite bo'lib qolsa, OperationalError ko'tarilishi shart."""
        with patch("moderation.selectors.connections") as mock_conns:
            mock_conns["default"].vendor = "sqlite"
            with pytest.raises(OperationalError, match="Bu modul faqat PostgreSQL'da ishlaydi"):
                _verify_postgres()


@pytest.mark.django_db
class TestModerationServicesAndTriggers:
    def test_report_and_approve_block_post_soft_deletes(self):
        author = User.objects.create_user(username="mod_author", password="pwd", okj_number=8101, okj_id="OKJ-8101")
        reporter = User.objects.create_user(username="mod_reporter", password="pwd", okj_number=8102, okj_id="OKJ-8102")
        moderator = User.objects.create_user(username="mod_staff", password="pwd", is_staff=True, okj_number=8103, okj_id="OKJ-8103")

        post = Post.objects.create(user=author, post_type=Post.PostType.QUOTE, content="Shubxali post matni", status=Post.Status.PUBLISHED)

        report = ModerationService.report_content(
            reporter=reporter,
            content_type=ContentReport.ContentType.POST,
            target_id=post.id,
            reason=ContentReport.ReportReason.SPAM,
            description="Spam reklama"
        )
        assert report.status == ContentReport.ReportStatus.PENDING

        # Moderator tasdiqlab bloklaydi
        resolved = ModerationService.resolve_report(
            moderator=moderator,
            report_id=report.id,
            action="APPROVE_AND_BLOCK",
            notes="Tasdiqlandi"
        )
        assert resolved.status == ContentReport.ReportStatus.RESOLVED

        # Post bazadan soft delete bo'lganligini tekshiramiz
        post.refresh_from_db()
        assert post.is_deleted is True
        assert post.moderation_status == Post.ModerationStatus.REJECTED

    def test_admin_toggle_shadow_ban(self):
        user = User.objects.create_user(username="shadow_user", password="pwd", okj_number=8104, okj_id="OKJ-8104")
        admin = User.objects.create_superuser(username="super_admin", password="pwd", okj_number=8105, okj_id="OKJ-8105")

        flag = ModerationService.admin_toggle_shadow_ban(user_id=user.id, is_ban=True, admin_user=admin)
        assert flag.is_shadow_banned is True
        assert flag.shadow_banned_by == admin

        flag_db = ModerationSelector.get_user_moderation_flag(user_id=user.id)
        assert flag_db is not None
        assert flag_db.is_shadow_banned is True


@pytest.mark.django_db
class TestModerationApis:
    def test_queue_access_denied_for_normal_users(self):
        normal_user = User.objects.create_user(username="normal_mod", password="pwd", okj_number=8106, okj_id="OKJ-8106")
        client = APIClient()
        client.force_authenticate(user=normal_user)

        response = client.get(reverse("moderation:queue"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_queue_access_allowed_for_staff_users(self):
        staff_user = User.objects.create_user(username="staff_mod", password="pwd", is_staff=True, okj_number=8107, okj_id="OKJ-8107")
        client = APIClient()
        client.force_authenticate(user=staff_user)

        response = client.get(reverse("moderation:queue"))
        assert response.status_code == status.HTTP_200_OK

    def test_report_content_api_and_resolve_api(self):
        author = User.objects.create_user(username="comment_author", password="pwd", okj_number=8108, okj_id="OKJ-8108")
        reporter = User.objects.create_user(username="comment_rep", password="pwd", okj_number=8109, okj_id="OKJ-8109")
        staff = User.objects.create_user(username="comment_staff", password="pwd", is_staff=True, okj_number=8110, okj_id="OKJ-8110")

        post = Post.objects.create(user=author, post_type=Post.PostType.QUOTE, content="Post")
        comment = Comment.objects.create(post=post, user=author, text="Yomon izoh matni")

        client = APIClient()
        client.force_authenticate(user=reporter)

        # 1. Shikoyat yuborish
        report_url = reverse("moderation:report")
        resp_report = client.post(report_url, {
            "content_type": "COMMENT",
            "target_id": str(comment.id),
            "reason": "HARASSMENT",
            "description": "Haqoratli so'z"
        }, format="json")
        assert resp_report.status_code == status.HTTP_201_CREATED
        report_id = resp_report.data["data"]["id"]

        # 2. Staff sifatida hal qilish
        client.force_authenticate(user=staff)
        resolve_url = reverse("moderation:resolve-report", kwargs={"id": report_id})
        resp_resolve = client.post(resolve_url, {
            "action": "APPROVE_AND_BLOCK",
            "notes": "Izoh o'chirildi"
        }, format="json")
        assert resp_resolve.status_code == status.HTTP_200_OK
        assert resp_resolve.data["data"]["status"] == "RESOLVED"

        comment.refresh_from_db()
        assert comment.is_deleted is True
        assert comment.is_approved is False
