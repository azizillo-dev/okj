"""
OKJ PLATFORM - POSTS MODELS (apps/posts/models.py)
Nega bu fayl kerak: Kitobxonlarning iqtiboslari, taqrizlari, ko'rgazma rasmlari,
kitob almashish/sotish e'lonlari hamda moderatsiya holatlarini bazada saqlash.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from books.models import Book
from library.models import LibraryItem
from accounts.models import District
from .validators import validate_review_rating, validate_media_order
from .managers import ActivePostManager, PublishedPostManager, DraftPostManager


class Post(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    OKJ Ijtimoiy tarmoq tasmadagi universal post modeli (Instagram / Goodreads usuli).
    """
    class PostType(models.TextChoices):
        QUOTE = "QUOTE", "Iqtibos"
        REVIEW = "REVIEW", "Kitob taqrizi"
        SHOWCASE = "SHOWCASE", "Ko'rgazma (Rasm)"
        EXCHANGE = "EXCHANGE", "Kitob almashish"
        GIFT = "GIFT", "Kitob sovg'a qilish"
        SELL = "SELL", "Kitob sotish"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Qoralama"
        PUBLISHED = "PUBLISHED", "Chop etilgan"
        SCHEDULED = "SCHEDULED", "Rejalashtirilgan"
        ARCHIVED = "ARCHIVED", "Arxivlangan"

    class ModerationStatus(models.TextChoices):
        PENDING = "PENDING", "Tekshirilmoqda"
        APPROVED = "APPROVED", "Tasdiqlangan"
        REJECTED = "REJECTED", "Rad etilgan"

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Barchaga ochiq"
        FOLLOWERS_ONLY = "FOLLOWERS_ONLY", "Faqat obunachilarga"
        PRIVATE = "PRIVATE", "Faqat o'zimga"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    post_type = models.CharField(max_length=20, choices=PostType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    moderation_status = models.CharField(
        max_length=20, choices=ModerationStatus.choices, default=ModerationStatus.APPROVED, db_index=True
    )
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    # Content fields
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True, help_text="Asosiy matn / taqriz")
    quote_text = models.TextField(blank=True, help_text="Iqtibos matni")
    quote_page = models.PositiveIntegerField(null=True, blank=True, help_text="Kitobning nechanchi betidan")
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[validate_review_rating])

    # Relations
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    library_item = models.ForeignKey(
        LibraryItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )

    # Meta & Discovery
    hashtags = models.CharField(max_length=500, blank=True, help_text="m-n: #uzbekistan #kitob #navoiy")
    mentions = models.CharField(max_length=500, blank=True, help_text="m-n: @bobur @azizillo")
    slug = models.SlugField(max_length=300, unique=True, db_index=True)
    views_count = models.PositiveIntegerField(default=0)

    # Dates
    publish_at = models.DateTimeField(null=True, blank=True, help_text="Rejalashtirilgan vaqt")
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Managers
    objects = ActivePostManager()
    published_objects = PublishedPostManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Postlar"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "moderation_status", "is_deleted", "-published_at"], name="idx_post_feed"),
            models.Index(fields=["user", "post_type", "-created_at"], name="idx_post_user_type"),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.post_type} ({self.status})"


class PostMedia(TimeStampedModel):
    """
    Postga ilova qilingan rasmlar galereyasi (Instagram carousel usuli).
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    image_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0, validators=[validate_media_order])

    class Meta:
        verbose_name = "Post Rasmi (Media)"
        verbose_name_plural = "Post Rasmlari"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.post.id} — Rasm #{self.order}"


class PostReport(TimeStampedModel):
    """
    Post ustidan shikoyat qilish (Moderation Report System).
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reports")
    reason = models.CharField(max_length=255, help_text="Shikoyat sababi")
    details = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Shikoyat (Report)"
        verbose_name_plural = "Shikoyatlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> Post {self.post.id} ({self.reason})"


class DraftPost(Post):
    """
    Faqat qoralamalar (DRAFT) bilan ishlash uchun Proxy Model.
    Nega kerak: Admin paneli va selektorlarda qoralamalarni alohida boshqarish.
    """
    objects = DraftPostManager()

    class Meta:
        proxy = True
        verbose_name = "Qoralama Post"
        verbose_name_plural = "Qoralama Postlar"


class PostViewCounter(TimeStampedModel):
    """
    Postning ko'rishlar sonini 1-to-1 saqlovchi jadval.
    """
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="view_counter", primary_key=True)
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Post Ko'rishlar Hisoblagichi"
        verbose_name_plural = "Post Ko'rishlar Hisoblagichlari"

    def __str__(self):
        return f"{self.post.id} — {self.total_views} views"
