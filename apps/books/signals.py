"""
OKJ PLATFORM - BOOKS SIGNALS (apps/books/signals.py)
Nega bu fayl kerak: Kitoblar saqlanganda kashlarni tozalash yoki
statistika jadvallarini avtomat sinxronizatsiya qilish.
"""

import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector, Value
from .models import Book, BookStatistics

logger = logging.getLogger(__name__)


def _update_book_search_vector(book_id):
    """Yordamchi funksiya: Kitobning title (A vazn) va authors__name (B vazn) bo'yicha search_vector ni hisoblash."""
    try:
        book = Book.objects.filter(id=book_id).first()
        if not book:
            return
        authors_str = " ".join(book.authors.filter(is_deleted=False).values_list("name", flat=True))
        vector = SearchVector("title", weight="A")
        if authors_str:
            vector = vector + SearchVector(Value(authors_str), weight="B")
        Book.objects.filter(id=book.id).update(search_vector=vector)
    except Exception as e:
        logger.error(f"Error updating search_vector for book {book_id}: {e}")


@receiver(post_save, sender=Book)
def ensure_book_statistics_and_search_vector(sender, instance: Book, created: bool, **kwargs):
    """Kitob yaratilsa yoki yangilansa, uning statistika jadvali va search_vector ustunini yangilash."""
    if created:
        BookStatistics.objects.get_or_create(book=instance)
        logger.info(f"Katalogga yangi kitob qo'shildi: {instance.title} ({instance.isbn_13 or 'No ISBN'})")
    _update_book_search_vector(instance.id)


@receiver(m2m_changed, sender=Book.authors.through)
def update_book_search_vector_on_authors_change(sender, instance, action, **kwargs):
    """Mualliflar o'zgarganda search_vector ustunini avtomat yangilash."""
    if action in ["post_add", "post_remove", "post_clear"]:
        if isinstance(instance, Book):
            _update_book_search_vector(instance.id)
