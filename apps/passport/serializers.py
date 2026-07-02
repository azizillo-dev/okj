"""
OKJ PLATFORM - PASSPORT SERIALIZERS (apps/passport/serializers.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha ma'lumotlarni
API ko'rinishida transport qilish uchun toza transport qatlami.
"""

from rest_framework import serializers


class ReadingPassportSerializer(serializers.Serializer):
    """Kitobxonning shaxsiy elektron pasport ma'lumotlari serializatori."""
    okj_id = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    total_xp = serializers.IntegerField()
    level = serializers.IntegerField()
    rank = serializers.IntegerField()
    total_books_finished = serializers.IntegerField()
    total_pages_read = serializers.IntegerField()
    top_genre = serializers.CharField(allow_null=True)
    top_language = serializers.CharField(allow_null=True)


class LeaderboardItemSerializer(serializers.Serializer):
    """Global peshqadamlar ro'yxati qatori serializatori."""
    rank = serializers.IntegerField()
    username = serializers.CharField()
    total_xp = serializers.IntegerField()
    level = serializers.IntegerField()
