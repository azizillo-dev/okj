"""
OKJ PLATFORM - POSTS SERVICES (apps/posts/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari
va biznes qoidalarni (30 daqiqa tahrir cheklovi, Iqtibos/Taqriz shartlari)
nazorat qilish @transaction.atomic ostida bajariladi.
"""

from typing import Optional, List, Dict, Any
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.text import slugify
from core.exceptions import ApplicationError
from books.selectors import BookSelector
from shared.services import BaseService
from .models import Post, PostMedia, PostReport, PostViewCounter
from .validators import check_media_edit_timeframe


class PostService(BaseService):
    """Postlar yaratish, tahrirlash, chop etish va moderatsiya servisi."""

    @classmethod
    def _validate_business_rules(
        cls,
        post_type: str,
        status: str,
        district_id: Optional[int],
        quote_text: str,
        user_rating: Optional[int],
        media_count: int,
    ):
        """
        OKJ Biznes qoidalarini tekshirish:
        1. Exchange/Sell postlari uchun tuman (district) shart.
        2. Quote postlari uchun iqtibos matni (quote_text) shart.
        3. Review postlari uchun baho (user_rating) shart.
        4. Showcase postlar chop etilganda kamida 1 ta rasm shart.
        """
        if post_type in [Post.PostType.EXCHANGE, Post.PostType.SELL] and not district_id:
            raise ApplicationError(
                "Kitob almashish (Exchange) yoki sotish (Sell) e'lonlari uchun tuman ko'rsatilishi shart.",
                code="DISTRICT_REQUIRED",
            )
        if post_type == Post.PostType.QUOTE and not quote_text.strip():
            raise ApplicationError(
                "Iqtibos (Quote) postlari uchun iqtibos matni kiritilishi shart.",
                code="QUOTE_TEXT_REQUIRED",
            )
        if post_type == Post.PostType.REVIEW and user_rating is None:
            raise ApplicationError(
                "Kitob taqrizi (Review) uchun baho (1-5) qo'yilishi shart.",
                code="RATING_REQUIRED",
            )
        if status == Post.Status.PUBLISHED and post_type == Post.PostType.SHOWCASE and media_count == 0:
            raise ApplicationError(
                "Ko'rgazma (Showcase) postlarini chop etish uchun kamida 1 ta rasm bo'lishi shart.",
                code="SHOWCASE_IMAGE_REQUIRED",
            )

    @classmethod
    def _generate_unique_slug(cls, title: str, post_type: str) -> str:
        base_text = title if title.strip() else f"post-{post_type.lower()}"
        slug = slugify(base_text) or f"okj-{post_type.lower()}"
        unique_slug = slug
        counter = 1
        while Post.all_objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{counter}"
            counter += 1
        return unique_slug

    @classmethod
    @transaction.atomic
    def create_post(
        cls,
        user,
        post_type: str,
        status: str = Post.Status.DRAFT,
        title: str = "",
        content: str = "",
        quote_text: str = "",
        quote_page: Optional[int] = None,
        user_rating: Optional[int] = None,
        book_id: Optional[str] = None,
        library_item_id: Optional[str] = None,
        district_id: Optional[int] = None,
        hashtags: str = "",
        mentions: str = "",
        visibility: str = Post.Visibility.PUBLIC,
        publish_at: Optional[Any] = None,
        media_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Post:
        """Yangi post yoki qoralama yaratish."""
        media_list = media_items or []
        target_district_id = district_id or (user.district_id if hasattr(user, "district_id") else None)

        cls._validate_business_rules(
            post_type=post_type,
            status=status,
            district_id=target_district_id,
            quote_text=quote_text,
            user_rating=user_rating,
            media_count=len(media_list),
        )

        slug = cls._generate_unique_slug(title=title or content[:30], post_type=post_type)
        published_at = timezone.now() if status == Post.Status.PUBLISHED else None

        post = Post.objects.create(
            user=user,
            post_type=post_type,
            status=status,
            title=title,
            content=content,
            quote_text=quote_text,
            quote_page=quote_page,
            user_rating=user_rating,
            book_id=book_id,
            library_item_id=library_item_id,
            district_id=target_district_id,
            hashtags=hashtags,
            mentions=mentions,
            visibility=visibility,
            slug=slug,
            publish_at=publish_at,
            published_at=published_at,
        )

        PostViewCounter.objects.get_or_create(post=post)

        # Media rasmlarini qo'shish
        for idx, media_data in enumerate(media_list):
            PostMedia.objects.create(
                post=post,
                image_url=media_data["image_url"],
                caption=media_data.get("caption", ""),
                order=media_data.get("order", idx),
            )

        # Agar chop etilgan bo'lsa kitobxon XP si va statistikasi yangilanadi
        if status == Post.Status.PUBLISHED:
            from accounts.services import UserService
            UserService.add_xp(user=user, amount=15, reason=f"Yangi {post_type} post chop etildi")

        return post

    @classmethod
    @transaction.atomic
    def update_post(
        cls,
        post: Post,
        title: Optional[str] = None,
        content: Optional[str] = None,
        quote_text: Optional[str] = None,
        quote_page: Optional[int] = None,
        user_rating: Optional[int] = None,
        district_id: Optional[int] = None,
        hashtags: Optional[str] = None,
        mentions: Optional[str] = None,
        visibility: Optional[str] = None,
        media_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Post:
        """Mavjud postni tahrirlash (30 daqiqalik media qoidasi bilan)."""
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        if quote_text is not None:
            post.quote_text = quote_text
        if quote_page is not None:
            post.quote_page = quote_page
        if user_rating is not None:
            post.user_rating = user_rating
        if district_id is not None:
            post.district_id = district_id
        if hashtags is not None:
            post.hashtags = hashtags
        if mentions is not None:
            post.mentions = mentions
        if visibility is not None:
            post.visibility = visibility

        # Agar rasmlar yangilanayotgan bo'lsa, 30 daqiqalik cheklovni nazorat qilamiz
        if media_items is not None:
            if post.status == Post.Status.PUBLISHED:
                check_media_edit_timeframe(post.published_at)

            post.media.all().delete()
            for idx, media_data in enumerate(media_items):
                PostMedia.objects.create(
                    post=post,
                    image_url=media_data["image_url"],
                    caption=media_data.get("caption", ""),
                    order=media_data.get("order", idx),
                )

        cls._validate_business_rules(
            post_type=post.post_type,
            status=post.status,
            district_id=post.district_id,
            quote_text=post.quote_text,
            user_rating=post.user_rating,
            media_count=post.media.count(),
        )

        post.full_clean()
        post.save()
        return post

    @classmethod
    @transaction.atomic
    def publish_post(cls, post: Post) -> Post:
        """Qoralamani chop etish."""
        cls._validate_business_rules(
            post_type=post.post_type,
            status=Post.Status.PUBLISHED,
            district_id=post.district_id,
            quote_text=post.quote_text,
            user_rating=post.user_rating,
            media_count=post.media.count(),
        )
        post.status = Post.Status.PUBLISHED
        post.published_at = timezone.now()
        post.save(update_fields=["status", "published_at"])

        from accounts.services import UserService
        UserService.add_xp(user=post.user, amount=15, reason=f"{post.post_type} post chop etildi")
        return post

    @classmethod
    @transaction.atomic
    def archive_post(cls, post: Post) -> Post:
        """Postni arxivga o'tkazish."""
        post.status = Post.Status.ARCHIVED
        post.save(update_fields=["status"])
        return post

    @classmethod
    @transaction.atomic
    def soft_delete_post(cls, post: Post) -> None:
        """Postni soft delete qilish."""
        post.is_deleted = True
        post.deleted_at = timezone.now()
        post.save(update_fields=["is_deleted", "deleted_at"])

    @classmethod
    @transaction.atomic
    def report_post(cls, user, post: Post, reason: str, details: str = "") -> PostReport:
        """Post ustidan moderatsiyaga shikoyat yozish."""
        return PostReport.objects.create(post=post, user=user, reason=reason, details=details)

    @classmethod
    def increment_post_views(cls, post: Post) -> None:
        """Post ko'rilganda view hisoblagichini oshirish."""
        Post.objects.filter(id=post.id).update(views_count=F("views_count") + 1)
        PostViewCounter.objects.filter(post_id=post.id).update(
            total_views=F("total_views") + 1, unique_views=F("unique_views") + 1
        )
