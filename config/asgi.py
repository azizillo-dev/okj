"""
ASGI config for OKJ project.
Nega kerak: Realtime WebSocket (Chat & Notifications) va asinxron HTTP so'rovlar (Daphne) uchun.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Django sozlamalarini yuklab olamiz
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket marshrutlari keyinchalik kelajakdagi chat va notification applaridan qo'shiladi
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Bo'sh marshrut (biznes modullar qo'shilganda to'ldiriladi)
        ])
    ),
})
