"""
OKJ PLATFORM - SHARED TEXT CHOICES (shared/choices.py)
Nega bu fayl kerak: Barcha app'larda takrorlanuvchi til, jins va umumiy holat 
tanlovlarini yagona joyda saqlash.
"""

from django.db import models


class LanguageChoices(models.TextChoices):
    UZBEK = "uz", "O'zbekcha"
    RUSSIAN = "ru", "Русский"
    ENGLISH = "en", "English"


class GenderChoices(models.TextChoices):
    MALE = "MALE", "Erkak"
    FEMALE = "FEMALE", "Ayol"
    UNSPECIFIED = "UNSPECIFIED", "Ko'rsatilmadi"
