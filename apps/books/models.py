"""
OKJ PLATFORM - BOOKS DOMAIN MODELS (apps/books/models.py)
Nega bu fayl kerak: O'zbekistondagi eng yagona va toza adabiyotlar katalogi,
mualliflar, janrlar, nashriyotlar va statistika jadvallarini saqlash.
"""

from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from .validators import (
    validate_isbn_10,
    validate_isbn_13,
    validate_publication_year,
    validate_cover_image_url_or_extension,
)
from .managers import ActiveBookManager, VerifiedBookManager


class Author(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Kitob muallifi modeli.
    Nega UUID: URL orqali muallif sahifalariga tezkor o'tish va xavfsizlik.
    """
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    bio = models.TextField(blank=True)
    birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
    death_year = models.PositiveSmallIntegerField(null=True, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    objects = ActiveBookManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Muallif"
        verbose_name_plural = "Mualliflar"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name", "is_deleted"]),
        ]

    def __str__(self):
        return self.name


class Genre(TimeStampedModel, SoftDeleteModel):
    """
    Kitob janri modeli (Ierarxik - ota-bola janrlar).
    m-n: Badiiy adabiyot -> Detektiv -> Psixologik detektiv.
    """
    name = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=180, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subgenres",
    )

    objects = ActiveBookManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Janr"
        verbose_name_plural = "Janrlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Publisher(TimeStampedModel, SoftDeleteModel):
    """
    Kitob nashriyoti modeli (m-n: Asaxiy Books, Akademnashr, Yangi Asr Avlodi).
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    country = models.CharField(max_length=100, default="O'zbekiston")
    website = models.URLField(max_length=255, blank=True, null=True)

    objects = ActiveBookManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Nashriyot"
        verbose_name_plural = "Nashriyotlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Language(TimeStampedModel):
    """
    Adabiyot tili (m-n: uz, ru, en, tr).
    """
    code = models.CharField(max_length=10, unique=True, db_index=True, help_text="m-n: uz")
    name = models.CharField(max_length=100, help_text="m-n: O'zbek tili")
    native_name = models.CharField(max_length=100, help_text="m-n: O'zbekcha")

    class Meta:
        verbose_name = "Til"
        verbose_name_plural = "Tillar"
        ordering = ["code"]

    def __str__(self):
        return self.name


class Book(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    OKJ Katalogidagi asosiy Kitob modeli.
    Nega barcha ma'lumotlar bor: Kuratorlar tekshirgan toza adabiy pasport vazifasini o'taydi.
    """
    class VerificationStatus(models.TextChoices):
        DRAFT = "DRAFT", "Qoralama (Foydalanuvchi qo'shgan)"
        VERIFIED = "VERIFIED", "Tasdiqlangan (Kurator tekshirgan)"
        REJECTED = "REJECTED", "Rad etilgan"
        ARCHIVED = "ARCHIVED", "Arxivlangan"

    # Identifiers
    isbn_10 = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        validators=[validate_isbn_10],
        db_index=True,
    )
    isbn_13 = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        validators=[validate_isbn_13],
        db_index=True,
    )

    # Content
    title = models.CharField(max_length=300, db_index=True)
    original_title = models.CharField(max_length=300, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=350, unique=True, db_index=True)

    # Publishing Info
    publication_year = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_publication_year]
    )
    page_count = models.PositiveSmallIntegerField(null=True, blank=True)
    language = models.ForeignKey(
        Language, on_delete=models.PROTECT, related_name="books", null=True, blank=True
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, related_name="books", null=True, blank=True
    )

    # Relations
    genres = models.ManyToManyField(Genre, related_name="books")
    authors = models.ManyToManyField(Author, related_name="books")

    # Media & Search
    cover_image = models.URLField(
        max_length=500, blank=True, validators=[validate_cover_image_url_or_extension]
    )
    search_keywords = models.CharField(max_length=500, blank=True, help_text="Tezkor qidiruv so'zlari")
    search_vector = SearchVectorField(null=True, db_index=True)

    # Cache Counters (Tezkor o'qish uchun)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, db_index=True)
    ratings_count = models.PositiveIntegerField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    reading_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)

    # Status
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.DRAFT,
        db_index=True,
    )

    # Managers
    objects = ActiveBookManager()
    verified_objects = VerifiedBookManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=Q(page_count__gte=1) | Q(page_count__isnull=True), name="check_positive_page_count"),
            models.CheckConstraint(check=Q(average_rating__gte=0.00) & Q(average_rating__lte=5.00), name="check_rating_range"),
            models.UniqueConstraint(fields=["isbn_13"], condition=Q(isbn_13__isnull=False) & ~Q(isbn_13=""), name="unique_isbn_13_not_null"),
            models.UniqueConstraint(fields=["isbn_10"], condition=Q(isbn_10__isnull=False) & ~Q(isbn_10=""), name="unique_isbn_10_not_null"),
        ]
        indexes = [
            models.Index(fields=["verification_status", "is_deleted", "-average_rating"], name="idx_book_verified_rating"),
            models.Index(fields=["verification_status", "-created_at"], name="idx_book_status_created"),
            GinIndex(fields=["search_vector"], name="idx_book_search_vector"),
        ]

    def __str__(self):
        return self.title


class BookEdition(UUIDModel, TimeStampedModel):
    """
    Kitobning boshqa nashrlari (m-n: qattiq muqova, yubiley nashri yoki boshqa nashriyot varianti).
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="editions")
    edition_name = models.CharField(max_length=200, help_text="m-n: 2-nashr, Qattiq muqovali")
    isbn_13 = models.CharField(max_length=17, blank=True, null=True, validators=[validate_isbn_13])
    isbn_10 = models.CharField(max_length=13, blank=True, null=True, validators=[validate_isbn_10])
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    publication_year = models.PositiveSmallIntegerField(null=True, blank=True)
    page_count = models.PositiveSmallIntegerField(null=True, blank=True)
    cover_image = models.URLField(max_length=500, blank=True)

    class Meta:
        verbose_name = "Kitob Nashri"
        verbose_name_plural = "Kitob Nashrlari"

    def __str__(self):
        return f"{self.book.title} ({self.edition_name})"


class BookCover(TimeStampedModel):
    """
    Kitobning muqova rasmlari galereyasi (Old, Orqa, va Ichki sahifalar rasmlari).
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="covers")
    cover_url = models.URLField(max_length=500, validators=[validate_cover_image_url_or_extension])
    caption = models.CharField(max_length=200, blank=True, help_text="m-n: Old muqova")
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Kitob Muqovasi"
        verbose_name_plural = "Kitob Muqovalari"

    def __str__(self):
        return f"{self.book.title} — {self.caption or 'Rasm'}"


class BookStatistics(TimeStampedModel):
    """
    Kitobning 1-to-1 batafsil analitikasi va mashhurlik indeksi (Popularity Score).
    Nega alohida: Lenta qidiruvini og'irlashtirmasdan, cron tasklar orqali mashhurlikni hisoblash.
    """
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="statistics", primary_key=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    ratings_count = models.PositiveIntegerField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    reading_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    popularity_score = models.FloatField(default=0.0, db_index=True)

    class Meta:
        verbose_name = "Kitob Statistikasi"
        verbose_name_plural = "Kitob Statistikalari"

    def __str__(self):
        return f"{self.book.title} (Popularity: {self.popularity_score:.1f})"
