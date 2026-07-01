"""
OKJ PLATFORM - ACCOUNTS SERIALIZERS (apps/accounts/serializers.py)
Nega bu fayl kerak: HTTP JSON so'rovlarini validatsiya qilish va
modellarimizni chiroyli API javoblariga aylantirib berish.
"""

from rest_framework import serializers
from .models import User, District
from .validators import validate_phone_number_format


class DistrictSerializer(serializers.ModelSerializer):
    """Viloyat va Tumanlar uchun oddiy va yengil serializer."""
    class Meta:
        model = District
        fields = ("id", "name", "region_name")


class ReaderProfileReadSerializer(serializers.ModelSerializer):
    """Kitobxonning to'liq profilini (district bilan birga) qaytaruvchi serializer."""
    district = DistrictSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    is_curator = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "okj_id",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "avatar_url",
            "bio",
            "district",
            "total_xp",
            "current_streak",
            "highest_streak",
            "role",
            "is_curator",
            "created_at",
        )


class ReaderRegisterSerializer(serializers.Serializer):
    """Ro'yxatdan o'tkazish uchun kiruvchi JSON payload."""
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number_format])
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    district_id = serializers.IntegerField(required=False, allow_null=True)
    google_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)


class ReaderProfileUpdateSerializer(serializers.Serializer):
    """Profilni tahrirlash uchun kiruvchi payload."""
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    avatar_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
    district_id = serializers.IntegerField(required=False, allow_null=True)
