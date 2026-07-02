"""
OKJ PLATFORM - BOOKS ADMIN PANEL (apps/books/admin.py)
Nega bu fayl kerak: Boshqaruv paneli orqali kuratorlar kitoblarni
1 klik bilan tasdiqlashi (bulk verify) yoki arxivlashini ta'minlash.
"""

from django.contrib import admin
from django.contrib import messages
from .models import Author, Genre, Publisher, Language, Book, BookEdition, BookCover


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "birth_year", "death_year", "is_deleted")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("is_deleted",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "is_deleted")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent", "is_deleted")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "website")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "native_name")
    search_fields = ("code", "name")


class BookCoverInline(admin.TabularInline):
    model = BookCover
    extra = 1


class BookEditionInline(admin.TabularInline):
    model = BookEdition
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "isbn_13",
        "publisher",
        "language",
        "average_rating",
        "reading_count",
        "verification_status",
        "is_deleted",
    )
    list_filter = ("verification_status", "is_deleted", "language", "genres")
    search_fields = ("title", "isbn_13", "isbn_10", "authors__name")
    readonly_fields = ("id", "slug", "average_rating", "ratings_count", "reviews_count", "reading_count", "favorites_count", "created_at", "updated_at")
    filter_horizontal = ("authors", "genres")
    inlines = [BookCoverInline, BookEditionInline]
    actions = ["bulk_verify_books", "bulk_archive_books"]

    fieldsets = (
        ("Asosiy Ma'lumotlar", {
            "fields": ("id", "title", "original_title", "subtitle", "slug", "description")
        }),
        ("ISBN va Nashr", {
            "fields": ("isbn_13", "isbn_10", "publication_year", "page_count", "language", "publisher")
        }),
        ("Mualliflar va Janrlar", {
            "fields": ("authors", "genres")
        }),
        ("Media va Qidiruv", {
            "fields": ("cover_image", "search_keywords")
        }),
        ("Statistika va Mashhurlik", {
            "fields": ("average_rating", "ratings_count", "reviews_count", "reading_count", "favorites_count")
        }),
        ("Status va Boshqaruv", {
            "fields": ("verification_status", "is_deleted", "created_at", "updated_at")
        }),
    )

    @admin.action(description="Tanlangan kitoblarni rasman TASDIQLASH (VERIFIED)")
    def bulk_verify_books(self, request, queryset):
        updated = queryset.update(verification_status=Book.VerificationStatus.VERIFIED)
        self.message_user(request, f"{updated} ta kitob muvaffaqiyatli tasdiqlandi.", messages.SUCCESS)

    @admin.action(description="Tanlangan kitoblarni ARXIVLASH (ARCHIVED)")
    def bulk_archive_books(self, request, queryset):
        updated = queryset.update(verification_status=Book.VerificationStatus.ARCHIVED)
        self.message_user(request, f"{updated} ta kitob arxivga o'tkazildi.", messages.WARNING)
