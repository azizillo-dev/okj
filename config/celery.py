import os
from celery import Celery

# Standart sozlamalarni 'local' ga yo'naltiramiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('okj_celery')

# Sozlamalarni Django settings.py faylidagi CELERY_ prefigi bilan yuklaymiz
app.config_from_object('django.conf:settings', namespace='CELERY')

# Barcha ro'yxatdan o'tgan app'lar ichidan tasks.py fayllarini avtomat qidiradi
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Celery Beat Periodik Tasks Sozlamasi (har 30 daqiqada lentalarni yangilash)
app.conf.beat_schedule = {
    "rebuild-all-active-feeds": {
        "task": "feed_ranking.rebuild_all_active_feeds_task",
        "schedule": 1800.0,  # 30 daqiqa
    },
}
