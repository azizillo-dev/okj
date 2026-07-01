"""
OKJ PLATFORM - ACCOUNTS MODELS (apps/accounts/models.py)
Nega bu fayl kerak: Barcha kitobxonlarning yagona identifikatori (OKJ-ID), 
geo-lokatsiyasi (Viloyat/Tuman) va intellektual statuslarini PostgreSQL da saqlash.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from .managers import ActiveUserManager
from .validators import validate_phone_number_format, validate_bio_content


class District(TimeStampedModel):
    """
    O'zbekistonning barcha viloyat va tumanlari ro'yxati.
    Nega kerak: Kitob almashtirishda p2p geo-filtrlash va lokal faollikni aniqlash.
    """
    name = models.CharField(max_length=100, db_index=True)
    region_name = models.CharField(max_length=100, db_index=True)

    class Meta:
        verbose_name = "Tuman / Shahar"
        verbose_name_plural = "Tumanlar va Shaharlar"
        constraints = [
            models.UniqueConstraint(fields=["region_name", "name"], name="unique_region_district")
        ]
        indexes = [
            models.Index(fields=["region_name", "name"]),
        ]

    def __str__(self):
        return f"{self.region_name} — {self.name}"


class User(AbstractUser, UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    OKJ Ekotizimining markaziy kitobxon modeli.
    Nega UUID: URL larda ID larni taxmin qila olmaslik uchun.
    Nega okj_id: Offline Book Festlarda, chipta va sovrinlarda inson o'qiydigan pasport raqami.
    """
    class Role(models.TextChoices):
        READER = "READER", "Kitobxon"
        CURATOR = "CURATOR", "Kurator (Kutubxonachi)"
        MODERATOR = "MODERATOR", "Moderator"
        ADMIN = "ADMIN", "Administrator"

    # Identity & Auth
    okj_id = models.CharField(
        max_length=16, 
        unique=True, 
        db_index=True, 
        help_text="m-n: OKJ-10492"
    )
    okj_number = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "Numerical OKJ raqami (m-n: 10492). "
            "Lexicographical saralash xavfini yo'qotish uchun alohida saqlanadi. "
            "okj_id = f'OKJ-{okj_number}' bilan sinxron bo'ladi."
        ),
    )
    phone_number = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[validate_phone_number_format],
        db_index=True
    )
    google_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        db_index=True
    )

    # Profile Profile & Geo
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, validators=[validate_bio_content])
    district = models.ForeignKey(
        District, 
        on_delete=models.PROTECT, 
        related_name="readers", 
        null=True, 
        blank=True
    )

    # Gamification & Streaks Cache
    total_xp = models.PositiveIntegerField(default=0, db_index=True)
    current_streak = models.PositiveIntegerField(default=0)
    highest_streak = models.PositiveIntegerField(default=0)

    # Permissions & Roles
    role = models.CharField(
        max_length=15, 
        choices=Role.choices, 
        default=Role.READER,
        db_index=True
    )

    # Managers
    objects = ActiveUserManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Kitobxon"
        verbose_name_plural = "Kitobxonlar"
        constraints = [
            models.CheckConstraint(check=Q(total_xp__gte=0), name="check_positive_total_xp"),
        ]
        indexes = [
            models.Index(fields=["district", "-total_xp"], name="idx_user_district_xp"),
            models.Index(fields=["role", "is_deleted"], name="idx_user_role_active"),
        ]

    def __str__(self):
        return f"{self.full_name or self.username} ({self.okj_id})"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_curator(self) -> bool:
        return self.role in [self.Role.CURATOR, self.Role.MODERATOR, self.Role.ADMIN] or self.is_superuser
