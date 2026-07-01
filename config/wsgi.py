"""
WSGI config for OKJ project.
Nega kerak: Sinxron HTTP so'rovlar (Gunicorn) orqali ishlashi uchun.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
