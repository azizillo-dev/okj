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
