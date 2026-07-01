"""
OKJ PLATFORM - FEED RANKING CELERY TASKS (apps/feed_ranking/tasks.py)
Nega bu fayl kerak: Lenta keshini yangilash va Fan-out operatsiyalari bazani yoki API'ni
to'sib qolmasligi uchun Celery asinxron tasklar sifatida bajariladi.

TASK ARXITEKTURASI:
1. rebuild_user_feed_cache_task: Bitta foydalanuvchi lentasini qayta hisoblash.
2. fan_out_post_to_followers_task: Yangi post yaratilganda Fan-out on Write.
3. rebuild_all_active_feeds_task: Celery Beat periodik vazifasi (masalan har 30 daqiqada).
"""

import logging
from celery import shared_task
from django.contrib.auth import get_user_model

from feed_ranking.services import FeedRankingService

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(
    name="feed_ranking.rebuild_user_feed_cache_task",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
)
def rebuild_user_feed_cache_task(user_id: str) -> int:
    """
    Bitta foydalanuvchi lentasini asinxron qayta hisoblash.

    Qachon chaqiriladi:
    - Cache Miss holatida (selektor fallback sifatida).
    - Foydalanuvchi yangi obunalikka qo'shilganda/olib tashlaganda.

    Args:
        user_id: Foydalanuvchi UUID (str formatida).
    Returns:
        Keshga yozilgan postlar soni.
    """
    count = FeedRankingService.generate_user_feed_cache(user_id)
    logger.info(f"Lenta keshi yangilandi: user_id={user_id}, jami={count} post")
    return count


@shared_task(
    name="feed_ranking.fan_out_post_to_followers_task",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=30,
)
def fan_out_post_to_followers_task(post_id: str, author_id: str) -> int:
    """
    Yangi post barcha obunachilarga (Followers) Fan-out on Write.

    Qachon chaqiriladi:
    - Yangi post chop etilganda (PostService.create_post / publish_post ilgagidan).

    Nima qiladi:
    - Post Score'ni hisoblaydi.
    - Keshi mavjud bo'lgan barcha obunachilarning Redis ZSET'iga ZADD orqali push.
    - Keshi yo'q obunachilar uchun isrof qilinmaydi (lazy loading).

    Args:
        post_id: Post UUID (str formatida).
        author_id: Muallif UUID (str formatida).
    Returns:
        Fan-out qilingan obunachilar soni.
    """
    count = FeedRankingService.fan_out_new_post(post_id=post_id, author_id=author_id)
    logger.info(f"Fan-out yakunlandi: post_id={post_id}, {count} ta obunachiga push qilindi")
    return count


@shared_task(
    name="feed_ranking.rebuild_all_active_feeds_task",
    autoretry_for=(Exception,),
    max_retries=2,
    retry_backoff=True,
    retry_backoff_max=120,
)
def rebuild_all_active_feeds_task() -> int:
    """
    Periodik Celery Beat vazifasi: So'nggi 7 kunda faol bo'lgan kitobxonlar
    lentalarini qayta hisoblash.

    Celery Beat sozlamasi (config/celery.py):
        app.conf.beat_schedule = {
            "rebuild-all-active-feeds": {
                "task": "feed_ranking.rebuild_all_active_feeds_task",
                "schedule": 1800.0,  # har 30 daqiqada
            },
        }

    Returns:
        Yangilangan foydalanuvchilar soni.
    """
    from datetime import timedelta
    from django.utils import timezone

    seven_days_ago = timezone.now() - timedelta(days=7)
    active_user_ids = list(
        User.objects.filter(
            is_active=True,
            is_deleted=False,
            last_login__gte=seven_days_ago,
        ).values_list("id", flat=True)
    )

    for user_id in active_user_ids:
        try:
            rebuild_user_feed_cache_task.delay(str(user_id))
        except Exception as e:
            logger.warning(f"Lenta yangilash task jo'natilmadi: user_id={user_id}, xato={e}")

    logger.info(f"Periodik lenta yangilash: {len(active_user_ids)} ta faol kitobxon")
    return len(active_user_ids)
