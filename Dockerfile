# ==============================================================================
# OKJ PLATFORM - PRODUCTION & LOCAL MULTI-STAGE DOCKERFILE
# Nega Python 3.12-slim: Minimal hajmli rasmiy konteyner, xavfsizlik va tezlik uchun.
# ==============================================================================
FROM python:3.12-slim as base

# Python sozlamalari
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Tizim kutubxonalarini o'rnatish (Postgres va c extensions uchun kerak)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Talab etilgan Python kutubxonalarini o'rnatish
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Loyiha kodini yuklash
COPY . /app/

# Portlarni ochish
EXPOSE 8000

# Standart ishga tushirish buyruqlari (docker-compose da qayta belgilanadi)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
