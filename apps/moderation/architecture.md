# OKJ Moderation & Trust and Safety Module — Me'moriy Hujjat (Architecture Blueprint)

## 1. Umumiy Ko'rinish
MODERATION moduli platformadagi kontentni (Post, Comment, Book) nazorat qilish, shikoyatlarni qabul qilish va ularni ko'rib chiqish navbatini (`Moderation Queue`) boshqarish, hamda qoidabuzar kitobxonlarga shadow ban qo'llashni markazlashgan tarzda ta'minlaydi.

---

## 2. Markazlashgan Shikoyat Tizimi (`ContentReport`)
Oldingi me'moriy modelda faqat Postlar uchun alohida `PostReport` (posts ilovasida) mavjud edi. Bu model yozilish va o'qishda tarqoqlikka olib kelardi.
- **Yangi yechim**: `apps/moderation/models.py` da yaratilgan `ContentReport` modeli `ContentType` (POST, COMMENT, BOOK) yordamida barcha kontent turlari uchun YAGONA shikoyat nuqtasiga aylandi.
- Eski `PostReport` modeli tarixiy ma'lumotlar uchun saqlab qolindi (Deprecated deb belgilandi), lekin barcha yangi so'rovlar (`ReportPostApi`) `ModerationService.report_content()` ga yo'naltirildi.

---

## 3. Moderatsiya Qarori (`RESOLVE`) va Soft-Delete Triggeri
Moderator (`is_staff=True` yoki `is_superuser=True`) shikoyatni ko'rib chiqqanda ikki turdagi qaror qabul qilishi mumkin:
1. **`APPROVE_AND_BLOCK`**:
   - Shikoyat qilingan kontent turiga qarab tegishli obyekt topiladi:
     - **POST**: `is_deleted = True`, `moderation_status = REJECTED`
     - **COMMENT**: `is_deleted = True`, `is_approved = False`
     - **BOOK**: `is_deleted = True`, `verification_status = REJECTED`
   - Bu o'zgarishlar barcha ijtimoiy lenta va selektorlarda ushbu kontentning avtomat yashirilishini (Soft Delete) ta'minlaydi.
2. **`DISMISS`**:
   - Shikoyat asossiz deb topilib, statusi `DISMISSED` holatiga o'tkaziladi.

---

## 4. Shadow Ban Arxitekturasi (`UserModerationFlag`)
HackSoft me'yorlari va mikroservislarga tayyorgarlik bo'yicha `accounts.User` modelining ichiga moderatsiya flaglarini qo'shish taqiqlandi.
- **Yechim**: `apps/moderation/models.py` da `UserModerationFlag` (OneToOne to User) jadvali yaratildi.
- Adminlar `admin_toggle_shadow_ban()` servisi orqali foydalanuvchining shadow ban holatini boshqaradi. Agar foydalanuvchida bu jadval bo'lmasa, `get_or_create` orqali dinamik yozuv yaratiladi va flag o'rnatiladi.

---

## 5. Ruxsatlar (Permissions) va Indekslar
- **Moderation Queue (`GET /api/v1/moderation/queue/`)**: Faqat `is_staff=True` yoki `is_superuser=True` xodimlarga ochiq. Oddiy foydalanuvchilarga `403 Forbidden` qaytariladi.
- **B-Tree Kompozit Indeks**: `(content_type, status, -created_at)` ustiga qo'yilgan indeks minglab shikoyatlar ichidan `PENDING` navbatini **O(log N)** tezlikda yuklab beradi.
