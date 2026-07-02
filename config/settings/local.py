"""
OKJ PLATFORM - LOCAL DEVELOPMENT SETTINGS (config/settings/local.py)
Nega bu fayl kerak: Dasturchining kompyuterida qulay ishlash, SQL so'rovlarni loglash
va CORS cheklovlarini yumshatish uchun.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Mahalliy ishlatishda SQLite yoki Docker Postgres
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Agar .env da DATABASE_URL ko'rsatilgan bo'lsa (m-n docker-compose dagi postgres)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES["default"] = dj_database_url.parse(DATABASE_URL)
    except ImportError:
        from urllib.parse import urlparse
        url = urlparse(DATABASE_URL)
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": url.path[1:],
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": url.port or 5432,
        }

# CORS local frontend (Next.js & Flutter Web) uchun ochiq
CORS_ALLOW_ALL_ORIGINS = True

# Email backend (mahally test uchun konsolga chiqaradi)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ==============================================================================
# TEST & LOCAL CACHE — LocMemCache (Redis ulangan bo'lmasa ham testlar ishlaydi)
# Nega: Test muhitida Redis o'chiq bo'lishi mumkin. django_redis o'rniga
# xotira keshi ishlatiladi. Throttling ham locmem bilan ishlaydi.
# ==============================================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "okj-local-cache",
    }
}

# ==============================================================================
# SENTRY ERROR TRACKING (Local - o'chirilgan, faqat SENTRY_DSN bo'lsa yoqiladi)
# ==============================================================================
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=False,
            before_send=sentry_before_send,
            environment="local",
        )
    except ImportError:
        pass
