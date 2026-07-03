"""
OKJ PLATFORM - DEMO DATA SEEDER
Nega kerak: Vercel frontend (Lenta va Pasport) bo'sh ko'rinmasligi uchun
namuna ma'lumotlarni (Kitoblar, Postlar, Iqtiboslar, Statistika) yaratadi.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from books.models import Book, Author, Genre, Language
from library.models import LibraryItem, UserReadingStatistic
from posts.models import Post


class Command(BaseCommand):
    help = "Vercel frontend uchun namunaviy kitoblar, pasport statistikasi va lenta postlarini yaratish"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Demo ma'lumotlar yaratish boshlandi..."))

        # 1. Foydalanuvchi topish yoki yaratish
        user = User.objects.filter(is_deleted=False).first()
        if not user:
            user = User.objects.create_user(
                username="nabiyev",
                password="okjPassword123!",
                first_name="Azizillo",
                last_name="Nabiyev",
                okj_id="OKJ-10492",
                total_xp=1450,
                streak_days=12,
            )
            self.stdout.write(self.style.SUCCESS(f"Yangi foydalanuvchi yaratildi: {user.username}"))
        else:
            if not user.okj_id:
                user.okj_id = "OKJ-10492"
            user.total_xp = 1450
            user.streak_days = 12
            user.save()

        # Statistika yaratish
        stats, _ = UserReadingStatistic.objects.get_or_create(user=user)
        stats.total_pages_read = 4982
        stats.total_books_read = 18
        stats.save()

        # 2. Janr va Til
        genre, _ = Genre.objects.get_or_create(name="Mumtoz adabiyot", defaults={"slug": "mumtoz-adabiyot"})
        lang, _ = Language.objects.get_or_create(code="uz", defaults={"name": "O'zbek tili"})
        author1, _ = Author.objects.get_or_create(name="Abdulla Qodiriy", defaults={"slug": "abdulla-qodiriy"})
        author2, _ = Author.objects.get_or_create(name="Alisher Navoiy", defaults={"slug": "alisher-navoiy"})

        # 3. Kitoblar
        book1, _ = Book.objects.get_or_create(
            slug="otkan-kunlar",
            defaults={
                "title": "O'tkan kunlar",
                "description": "O'zbek romanchiligining ilk va eng mashhur asari.",
                "page_count": 384,
                "language": lang,
            }
        )
        book1.authors.add(author1)
        book1.genres.add(genre)

        book2, _ = Book.objects.get_or_create(
            slug="xamsai-mutahayyirin",
            defaults={
                "title": "Xamsai Mutahayyirin",
                "description": "Buyuk shoir Alisher Navoiyning ustoziga bag'ishlab yozgan asari.",
                "page_count": 256,
                "language": lang,
            }
        )
        book2.authors.add(author2)
        book2.genres.add(genre)

        # 4. Library Item (O'qilgan qilib belgilash)
        LibraryItem.objects.get_or_create(
            user=user,
            book=book1,
            defaults={"status": LibraryItem.ReadingStatus.FINISHED, "current_page": 384}
        )
        LibraryItem.objects.get_or_create(
            user=user,
            book=book2,
            defaults={"status": LibraryItem.ReadingStatus.FINISHED, "current_page": 256}
        )

        # 5. Lenta Postlari (Feed)
        Post.objects.filter(slug="").delete()  # Toza holat uchun bo'sh slugli postni o'chiramiz
        if Post.objects.count() == 0:
            Post.objects.get_or_create(
                slug="otkan-kunlar-taqriz",
                defaults={
                    "user": user,
                    "book": book1,
                    "post_type": Post.PostType.REVIEW,
                    "title": "O'tkan kunlar — har safar yangicha taassurot",
                    "content": "Otabek va Kumushbibi muhabbati orqali o'zbek xalqining tarixiy qiyofasi mukammal ochib berilgan. Barcha yoshdagi kitobxonlarga o'qishni tavsiya etaman!",
                    "status": Post.Status.PUBLISHED,
                    "moderation_status": Post.ModerationStatus.APPROVED,
                    "published_at": timezone.now(),
                }
            )
            Post.objects.get_or_create(
                slug="navoiy-hikmatli-iqtibos",
                defaults={
                    "user": user,
                    "book": book2,
                    "post_type": Post.PostType.QUOTE,
                    "content": "«Odamiylik o'zgalar dardiga darmon bo'lishdan boshlanur...» — Alisher Navoiy satrlaridagi hikmat hstira qadrlidir.",
                    "status": Post.Status.PUBLISHED,
                    "moderation_status": Post.ModerationStatus.APPROVED,
                    "published_at": timezone.now(),
                }
            )
            Post.objects.get_or_create(
                slug="mehrobdan-chayon-almashish",
                defaults={
                    "user": user,
                    "post_type": Post.PostType.EXCHANGE,
                    "title": "«Mehrobdan chayon» kitobini almashtirmoqchiman",
                    "content": "Menda yangi holatdagi «Mehrobdan chayon» bor. Jahon adabiyoti klassikasidan biron kitobga almashaman. Toshkent shahar bo'ylab.",
                    "status": Post.Status.PUBLISHED,
                    "moderation_status": Post.ModerationStatus.APPROVED,
                    "published_at": timezone.now(),
                }
            )
            self.stdout.write(self.style.SUCCESS("3 ta namunaviy post lentaga qo'shildi!"))

        self.stdout.write(self.style.SUCCESS("Muvaffaqiyatli yakunlandi! Vercel pasport va lenta endi to'liq ishlaydi!"))
