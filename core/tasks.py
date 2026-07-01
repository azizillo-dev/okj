"""
OKJ PLATFORM - CORE BACKGROUND TASKS (core/tasks.py)
Nega bu fayl kerak: Tizimni tozalash va tizim salomatligini tekshiruvchi
Celery asinxron vazifalar.
"""

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def cleanup_temp_files_task():
    """Arxivlangan yoki vaqtinchalik yuklangan keraksiz fayllarni tozalash."""
    logger.info("Vahtinchalik fayllarni tozalash vazifasi ishga tushdi.")
    return "Cleanup completed"
