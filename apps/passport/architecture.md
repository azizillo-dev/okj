# OKJ Passport & Gamification Analytics Module — Me'moriy Hujjat (Architecture Blueprint)

## 1. Umumiy Ko'rinish
PASSPORT moduli Kitobxonning elektron o'qish pasportini, faollik darajasini (Level/XP), va platformadagi umumiy reyting o'rnini (Rank/Leaderboard) shakllantiradi. HackSoft me'yorlari hamda Meta/Duolingo masshtablanuvchanlik tajribasiga ko'ra, bu modul ortiqcha jonli agregatsiya (live query aggregation) va og'ir deraza funksiyalaridan (heavy window functions) holi ravishda O(1) va O(log N) tezlikda ishlaydi.

---

## 2. O'qish Statistikasi va `UserReadingStatistic` Kesh Jadvali
O'qib bo'lingan kitoblar soni (`total_books_finished`) va o'qilgan sahifalar (`total_pages_read`) har bir pasport so'rovida `LibraryItem` yoki `ReadingLog` jadvallaridan `SUM/COUNT` yordamida hisoblanmaydi.
- **Me'moriy yechim**: `apps/library/models.py` dagi `UserReadingStatistic` 1-to-1 jadvalidan to'g'ridan-to'g'ri `get_or_create` orqali o'qiladi. Har safar kitobxon yangi log yozganda yoki kitobni bitirganda, tranzaksiya ichida `select_for_update()` bilan ushbu kesh jadvali yangilanib turadi. Pasportni ochish esa **O(1)** vaqt talab qiladi.

---

## 3. Top Janr va Til Aniqlashda Fan-Out va N+1 Oldini Olish
Foydalanuvchi javonidagi `FINISHED` holatidagi kitoblarning janr va tili quyidagi ORM so'rovi orqali aniqlanadi:
```python
Genre.objects.filter(
    books__library_items__user=user,
    books__library_items__status=LibraryItem.ReadingStatus.FINISHED,
).annotate(count=Count("books__library_items", distinct=True)).order_by("-count", "name").first()
```
- **Nega `distinct=True`**: Kitoblar ko'p muallifli bo'lganda yoki bir necha marta JOIN bo'lganda, oddiy `Count()` fan-out tufayli sun'iy ko'p son hisoblab yuborishi mumkin. `distinct=True` faqat noyob yozuvlarni sanashni kafolatlaydi.

---

## 4. Leaderboard (Peshqadamlar Reytingi) va O'rin (Rank) Hisoblash
1. **Shaxsiy Rank**: Butun foydalanuvchilar jadvalini `ROW_NUMBER() OVER (ORDER BY total_xp DESC)` qilib saralash million yozuv bo'lganda bazani falokatga olib keladi. Buning o'rniga:
   ```python
   higher_xp_count = User.objects.filter(is_deleted=False, is_active=True, total_xp__gt=user.total_xp).count()
   rank = higher_xp_count + 1
   ```
   Bu `accounts_user` jadvalidagi `total_xp` indeksini (`db_index=True`) skanerlab, **O(log N)** tezlikda aniq o'rinni qaytaradi.
2. **Global Leaderboard**: TOP 50 ta kitobxonni qaytarishda qat'iy `[:50]` cheklovi qo'yilgan. View esa hech qanday biznes mantiqni o'zida saqlamaydi (Strict Thin Views).

---

## 5. Twelve-Factor & SQLite Cheklovi
Moduldagi barcha tahliliy so'rovlar va real PostgreSQL indeks skanerlash mantiqi `_verify_postgres()` nazoratidan o'tadi. SQLite muhitida ishga tushirilsa, `OperationalError` ko'tariladi.
