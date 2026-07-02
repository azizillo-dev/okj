# O'zbekiston Kitobxonlari Jamiyati (OKJ) — Backend Foundation

[![CI/CD Pipeline](https://github.com/azizillo-dev/okj/actions/workflows/ci.yml/badge.svg)](https://github.com/azizillo-dev/okj/actions/workflows/ci.yml)

Bu loyiha **O'zbekiston Kitobxonlari Jamiyati (OKJ)** platformasining **Professional Modular Monolith** dasturiy poydevori hisoblanadi.

## 🛠 Texnologiyalar
* **Python 3.12+** & **Django 5.0+**
* **Django REST Framework (DRF)** + SimpleJWT (HttpOnly & Secure Token Authentication)
* **PostgreSQL 16+** (Relational Database)
* **Redis 7+** (Caching, Celery Broker & Channels Realtime Layer)
* **Django Channels** (WebSocket Realtime Chat va Bildirishnomalar)
* **Cloudflare R2** (S3-mos keluvchi arzon va tezkor media xotira)
* **Docker & Docker Compose** (Yagona VPS serverda oson mashtablash)

---

## 📁 Papkalar Tuzilishi (HackSoft Styleguide)
```text
booklovers/
├── config/                 # Sozlamalar (base.py, local.py, production.py)
├── core/                   # Umumiy yordamchi modullar (pagination, exceptions, R2 storage)
├── shared/                 # HackSoft Styleguide mixinlar, enums, services base interfeysi
├── nginx/                  # Nginx Reverse Proxy va WebSocket sozlamalari
├── docker-compose.yml      # Barcha xizmatlar orkestratsiyasi
└── requirements.txt        # Loyiha qaramliklari
```

---

## 🚀 Mahalliy Muxitda Ishga Tushirish (Quick Start)

1. **.env fayl yaratish:**
   ```bash
   cp .env.example .env
   ```

2. **Docker Compose orqali barcha xizmatlarni ko'tarish:**
   ```bash
   docker compose up --build -d
   ```

3. **Migratsiya va Superuser yaratish:**
   ```bash
   docker exec -it okj_web python manage.py migrate
   docker exec -it okj_web python manage.py createsuperuser
   ```

4. **API Hujjatlarini ko'rish:**
   * Swagger UI: `http://localhost/api/docs/`
   * Redoc: `http://localhost/api/redoc/`
