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
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL)

# CORS local frontend (Next.js & Flutter Web) uchun ochiq
CORS_ALLOW_ALL_ORIGINS = True

# Email backend (mahally test uchun konsolga chiqaradi)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
