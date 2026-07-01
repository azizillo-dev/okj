"""
OKJ PLATFORM - PRODUCTION SETTINGS (config/settings/production.py)
Nega bu fayl kerak: Serverda maksimal xavfsizlik, Cloudflare R2 bulutli xotira
va yuqori unumdorlikni (Gunicorn/Daphne + Postgres connection pooling) ta'minlash.

KRITIK XAVFSIZLIK TEKSHIRUVLARI:
- Agar DJANGO_SECRET_KEY kiritilmagan yoki xavfsiz bo'lmasa, server ISHGA TUSHMAYDI.
- Agar POSTGRES_PASSWORD kiritilmagan bo'lsa, server ISHGA TUSHMAYDI.
"""

import os
from django.core.exceptions import ImproperlyConfigured
from .base import *
import dj_database_url

# ==============================================================================
# KRITIK ISHGA TUSHISH TEKSHIRUVLARI (Fail Fast)
# Nega kerak: Production serverda xavfsiz bo'lmagan sozlamalar bilan hech qachon
# ishga tushmaslik kerak. Muammolarni deploy vaqtida aniqlash runtime'dan yaxshiroq.
# ==============================================================================
_secret_key = os.getenv("DJANGO_SECRET_KEY", "")
if not _secret_key:
    raise ImproperlyConfigured(
        "PRODUCTION_ERROR: DJANGO_SECRET_KEY muhit o'zgaruvchisi o'rnatilmagan! "
        "Xavfsiz tasodifiy kalit yaratish uchun: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    )
if _secret_key.startswith("django-insecure"):
    raise ImproperlyConfigured(
        "PRODUCTION_ERROR: DJANGO_SECRET_KEY xavfsiz emas! "
        "Productionda 'django-insecure-' bilan boshlanuvchi kalit qabul qilinmaydi."
    )

if not os.getenv("POSTGRES_PASSWORD") and not os.getenv("DATABASE_URL"):
    raise ImproperlyConfigured(
        "PRODUCTION_ERROR: POSTGRES_PASSWORD yoki DATABASE_URL muhit o'zgaruvchisi o'rnatilmagan!"
    )

if not os.getenv("REDIS_PASSWORD"):
    raise ImproperlyConfigured(
        "PRODUCTION_ERROR: REDIS_PASSWORD muhit o'zgaruvchisi o'rnatilmagan! "
        "Redis xavfsizligi uchun kuchli parol o'rnating."
    )

DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "api.okj.uz").split(",")

# PostgreSQL Database (PgBouncer connection pooler bilan ishlashga tayyor)
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ==============================================================================
# CLOUDFLARE R2 STORAGE CONFIGURATION
# Nega R2: S3 ga qaraganda egress (trafik yuklab olish) narxi 0$ va juda tez.
# ==============================================================================
USE_CLOUDFLARE_R2 = os.getenv("USE_CLOUDFLARE_R2", "False").lower() == "true"

if USE_CLOUDFLARE_R2:
    R2_ACCOUNT_ID = os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")
    AWS_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    AWS_S3_CUSTOM_DOMAIN = os.getenv("CLOUDFLARE_R2_CUSTOM_DOMAIN")

    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# ==============================================================================
# SECURITY & CORS IN PRODUCTION
# HTTPS (Let's Encrypt + Nginx) muhitida ishlash uchun sozlamalar.
# SECURE_PROXY_SSL_HEADER: Nginx X-Forwarded-Proto sarlavhasini Django xavfsizlik
# tekshiruvlari uchun ishlatishga ruxsat beradi.
# ==============================================================================
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "https://okj.uz").split(",")
CORS_ALLOW_CREDENTIALS = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
