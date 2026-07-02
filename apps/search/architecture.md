# OKJ Global Search Module — Me'moriy Hujjat (Architecture Blueprint)

## 1. Umumiy Ko'rinish
OKJ (O'zbek Kitobxonlar Jamiyati) platformasida qidiruv mexanizmi **PostgreSQL Native Full-Text Search (FTS)** va **Trigram Similarity (`pg_trgm`)** texnologiyalari asosida qurilgan.
Katalog kattalashganda (100,000+ kitoblar va foydalanuvchilar) so'rov vaqtida hisoblash (Query-time calculation overhead) muammosini oldini olish uchun yassi ustun indekslash (**Stored Search Vector**) hamda **GIN (Generalized Inverted Index)** qo'llaniladi.

---

## 2. PostgreSQL Kengaytmalari (`pg_trgm` & `unaccent`)
Qidiruv tizimi ishlashi uchun PostgreSQL bazasida ikki muhim kengaytma faollashtiriladi (qaralsin: `books/migrations/0002_enable_pg_extensions.py`):
1. **`pg_trgm`**: Matnlarni 3 harfli bo'laklarga (trigrammalarga) ajratib, n-gram o'xshashlik hisoblaydi (`TrigramSimilarity`). Kitobxon so'zni imlo xatosi bilan yozsa ham (masalan, *"O'tkan kunlar"* o'rniga *"Otkan kunlar"* yoki *"Alisher Navoiy"* o'rniga *"Alisher Navoyi"*), 0.25–0.3 dan yuqori moslikka ega natijalarni topadi.
2. **`unaccent`**: Diakritik belgilarni, tutuq belgisi (') yoki chiziqchalarni tekshirishda farqlarni tekislaydi.

---

## 3. Stored `search_vector` va GIN Index
Kitoblar bo'yicha qidiruv har safar mualliflar va sarlavhani `JOIN` va `CONCAT` qilmasligi uchun `Book` modelida maxsus ustun mavjud:
```python
search_vector = SearchVectorField(null=True, db_index=True)
```
- **Vaznlar (Weights)**:
  - Kitob sarlavhasi (`title`): **A** vazn (eng yuqori ustuvorlik).
  - Mualliflar ismlari (`authors__name`): **B** vazn.
- **Avtomatik Sinxronizatsiya**: Kitob saqlanganda (`post_save`) yoki unga mualliflar bog'langanda (`m2m_changed`), `_update_book_search_vector` signali ishga tushib, `search_vector` ustunini va indeksni fonda yangilab qo'yadi.
- **Indekslash**: Ustun ustiga `GinIndex(fields=["search_vector"])` o'rnatilgan bo'lib, qidiruv natijalarini milisoniyalar ichida qaytaradi.

---

## 4. Selektor arxitekturasi va SQLite Cheklovi
HackSoft me'yorlariga asosan barcha qidiruv mantiqi `SearchSelector` sinfida (`apps/search/selectors.py`) joylashgan.
- **Twelve-Factor & Infrastructure Rule**: `_verify_postgres()` tekshiruvi orqali modul faqat PostgreSQL'da ishlashi qat'iy nazorat qilinadi. SQLite yoki boshqa relatsion bo'lmagan bazada ishga tushirilsa, `OperationalError` ko'tariladi.
