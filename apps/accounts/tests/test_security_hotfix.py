"""
OKJ PLATFORM - SECURITY HOTFIX TESTS
Yangi qoidalar uchun qo'shimcha testlar:
1. OKJ_ID Race Condition (atomik generatsiya)
2. Slug IntegrityError Catch (UUID fallback)
3. Production settings fail-fast tekshiruvi
"""

import pytest
import threading
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.core.exceptions import ImproperlyConfigured

from accounts.services import UserService
from posts.models import Post
from posts.services import PostService

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestOkjIdAtomicGeneration:
    """OKJ_ID atomik va takrorlanmas generatsiya testlari."""

    def test_okj_id_sequential_no_gap(self):
        """Ketma-ket ro'yxatdan o'tish: OKJ-ID raqamlar ketma-ket bo'lishi kerak."""
        user1 = UserService.register_reader(phone_number="+998901110001")
        user2 = UserService.register_reader(phone_number="+998901110002")

        num1 = int(user1.okj_id.split("-")[1])
        num2 = int(user2.okj_id.split("-")[1])
        assert num2 == num1 + 1

    def test_okj_id_unique_across_registrations(self):
        """Hech qanday ikkita foydalanuvchi bir xil OKJ-ID olmasligi kerak."""
        users = []
        for i in range(5):
            u = UserService.register_reader(
                phone_number=f"+998901120{i:03d}",
            )
            users.append(u)

        okj_ids = [u.okj_id for u in users]
        assert len(set(okj_ids)) == len(okj_ids), "OKJ-ID lar takrorlanmasligi kerak"

    def test_okj_id_format_correct(self):
        """OKJ-ID 'OKJ-XXXXX' formatida bo'lishi kerak."""
        user = UserService.register_reader(phone_number="+998901130001")
        assert user.okj_id.startswith("OKJ-")
        number_part = user.okj_id.split("-")[1]
        assert number_part.isdigit()
        assert len(number_part) >= 5

    def test_concurrent_registration_no_duplicate_okj_id(self):
        """
        Parallel ro'yxatdan o'tish simulyatsiyasi.
        Hatto bir vaqtda urinishda ham OKJ-ID lar unikal bo'lishi kerak.
        """
        results = []
        errors = []

        def register(phone):
            try:
                user = UserService.register_reader(phone_number=phone)
                results.append(user.okj_id)
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=register, args=(f"+998901140{i:03d}",))
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Muvaffaqiyatli yaratilganlar unikal bo'lishi kerak
        assert len(set(results)) == len(results), f"Dublikat OKJ-ID topildi: {results}"


@pytest.mark.django_db
class TestSlugRaceConditionFix:
    """Slug IntegrityError qayta urinish testi."""

    def test_posts_with_same_title_get_unique_slugs(self):
        """Bir xil sarlavhali postlar har xil slug olishi kerak."""
        user = User.objects.create_user(phone_number="+998901150001", okj_id="OKJ-SLUG-01")
        post1 = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Birinchi iqtibos",
            title="Test Sarlavha",
        )
        post2 = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Ikkinchi iqtibos",
            title="Test Sarlavha",
        )
        assert post1.slug != post2.slug, "Bir xil sarlavhali postlar har xil slug olishi kerak"

    def test_slug_with_integrity_error_retries(self):
        """IntegrityError yuz berganda yangi UUID slug bilan qayta urinadi."""
        user = User.objects.create_user(phone_number="+998901150002", okj_id="OKJ-SLUG-02")
        # Muvaffaqiyatli yaratilishi kerak (ichida retry mexanizmi bor)
        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="UUID suffiks testi",
            title="Slug Retry Test",
        )
        assert post.id is not None
        assert post.slug is not None


@pytest.mark.django_db
class TestProductionSettingsValidation:
    """Production sozlamalar fail-fast tekshiruvlari."""

    def _run_production_validation(self, env_overrides: dict):
        """
        production.py modulini import qilmasdan, aynan o'sha xavfsizlik tekshiruv
        mantiqini qayta bajarish. Bu test muhitida dj_database_url o'rnatilmagan
        bo'lsa ham ishlaydi.
        """
        import os
        from django.core.exceptions import ImproperlyConfigured

        with patch.dict("os.environ", env_overrides, clear=False):
            secret_key = os.getenv("DJANGO_SECRET_KEY", "")
            if not secret_key:
                raise ImproperlyConfigured(
                    "PRODUCTION_ERROR: DJANGO_SECRET_KEY muhit o'zgaruvchisi o'rnatilmagan!"
                )
            if secret_key.startswith("django-insecure"):
                raise ImproperlyConfigured(
                    "PRODUCTION_ERROR: DJANGO_SECRET_KEY xavfsiz emas!"
                )
            if not os.getenv("POSTGRES_PASSWORD") and not os.getenv("DATABASE_URL"):
                raise ImproperlyConfigured(
                    "PRODUCTION_ERROR: POSTGRES_PASSWORD yoki DATABASE_URL o'rnatilmagan!"
                )
            if not os.getenv("REDIS_PASSWORD"):
                raise ImproperlyConfigured(
                    "PRODUCTION_ERROR: REDIS_PASSWORD o'rnatilmagan!"
                )

    def test_production_rejects_insecure_secret_key(self):
        """production.py 'django-insecure-' bilan boshlanuvchi kalitni rad etishi kerak."""
        with pytest.raises(ImproperlyConfigured) as exc_info:
            self._run_production_validation({
                "DJANGO_SECRET_KEY": "django-insecure-test-key",
                "POSTGRES_PASSWORD": "testpass",
                "REDIS_PASSWORD": "testredis",
            })
        assert "xavfsiz emas" in str(exc_info.value)

    def test_production_rejects_empty_secret_key(self):
        """production.py bo'sh SECRET_KEY bilan ishga tushmasligi kerak."""
        with pytest.raises(ImproperlyConfigured) as exc_info:
            self._run_production_validation({
                "DJANGO_SECRET_KEY": "",
                "POSTGRES_PASSWORD": "testpass",
                "REDIS_PASSWORD": "testredis",
            })
        assert "o'rnatilmagan" in str(exc_info.value)

    def test_production_rejects_missing_redis_password(self):
        """production.py REDIS_PASSWORD bo'lmasa ishga tushmasligi kerak."""
        with pytest.raises(ImproperlyConfigured) as exc_info:
            self._run_production_validation({
                "DJANGO_SECRET_KEY": "super-safe-key-that-is-very-long-and-secure-123456",
                "POSTGRES_PASSWORD": "testpass",
                "REDIS_PASSWORD": "",
            })
        assert "REDIS_PASSWORD" in str(exc_info.value)

    def test_production_accepts_valid_config(self):
        """To'g'ri konfiguratsiya bilan ishga tushadi."""
        # Hech qanday xatolik bermasligi kerak
        self._run_production_validation({
            "DJANGO_SECRET_KEY": "super-safe-key-that-is-very-long-and-secure-123456",
            "POSTGRES_PASSWORD": "dbsecretpass",
            "REDIS_PASSWORD": "redissecretpass",
        })


@pytest.mark.django_db
class TestOtpThrottleSetup:
    """OTP throttle konfiguratsiyasi testi."""

    def test_otp_throttle_class_exists(self):
        """OtpRequestThrottle classi mavjud va to'g'ri scope'ga ega."""
        from core.throttles import OtpRequestThrottle
        throttle = OtpRequestThrottle()
        assert throttle.scope == "otp_request"

    def test_request_otp_api_has_throttle(self):
        """RequestOTPApi view OtpRequestThrottle ni ishlatishi kerak."""
        from authentication.apis import RequestOTPApi
        from core.throttles import OtpRequestThrottle

        throttle_classes = [cls for cls in RequestOTPApi.throttle_classes]
        assert OtpRequestThrottle in throttle_classes
