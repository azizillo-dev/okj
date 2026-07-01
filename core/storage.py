"""
OKJ PLATFORM - CLOUDFLARE R2 / AWS S3 STORAGE HELPER (core/storage.py)
Nega bu fayl kerak: Mobil ilova (Flutter) rasmlarni Django server orqali emas,
boto3 Presigned URL orqali to'g'ridan-to'g'ri Cloudflare R2 bulutiga yuklashi uchun.
"""

import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_presigned_upload_url(object_name: str, content_type: str = "image/jpeg", expiration_seconds: int = 300) -> Optional[Dict[str, Any]]:
    """
    Cloudflare R2 (S3) ga fayl yuklash uchun 5 daqiqali vaqtinchalik silsila va key yaratadi.
    """
    if not getattr(settings, "USE_CLOUDFLARE_R2", False):
        logger.warning("Cloudflare R2 sozlamasi o'chirilgan (USE_CLOUDFLARE_R2=False)")
        return None

    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        logger.error("boto3 kutubxonasi o'rnatilmagan.")
        return None

    r2_client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )

    try:
        response = r2_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=object_name,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 100, 10485760],  # 100 Bayt dan 10 MB gacha
            ],
            ExpiresIn=expiration_seconds,
        )
        return response
    except Exception as exc:
        logger.exception("Presigned URL generatsiya qilishda xatolik:", exc_info=exc)
        return None
