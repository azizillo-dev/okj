# OKJ Frontend & Backend API Audit Report

Bu hujjat OKJ platformasining frontend loyihasida aniqlangan barcha *mock, fallback, temporary, demo, va hardcoded* ma'lumotlarning ro'yxati va ularni Django REST Framework (DRF) real endpointlari bilan almashtirish (mapping) jadvalini o'z ichiga oladi.

---

## 📋 1. Endpoint Mapping jadvali

| Komponent / Sahifa | Hozirgi holati (Mock / Fallback) | Maqsadli Django DRF Endpoint | HTTP Metod | Izoh va Vazifalari |
| :--- | :--- | :--- | :--- | :--- |
| **`app/(auth)/login/page.tsx`** | Hardcode tekshiruv (`admin123`) yoki mock setTimeout | `/api/v1/auth/token/` | `POST` | JWT Access va Refresh tokenlarni olish, authStore va cookie'ga saqlash. |
| **`app/(auth)/register/page.tsx`** | Mock setTimeout ro'yxatdan o'tish | `/api/v1/auth/register/` | `POST` | Yangi kitobxonni ro'yxatdan o'tkazish va OTP tasdiqqa yuborish. |
| **`app/feed/page.tsx`** | `catch` block ichida 3 ta demo post qoldirilgan | `/api/v1/posts/?page={page}&type={type}` | `GET` | TanStack Infinite Query bilan paginatsiya va real postlarni tortish. |
| **`app/books/[slug]/page.tsx`** | `catch` block ichida demo kitob obyektlari | `/api/v1/books/{slug}/` | `GET` | Kitob haqida to'liq ma'lumot, reyting va mualliflarni API orqali olish. |
| **`app/posts/[id]/page.tsx`** | `sampleComments` va demo `samplePost` | `/api/v1/posts/{id}/` va `/api/v1/comments/?post_id={id}` | `GET` | Postning to'liq tafsiloti va uning fikr-mulohazalarini (nested replies) olish. |
| **`app/search/page.tsx`** | Statik array `demoBooks` | `/api/v1/search/?q={query}&filter={filter}` | `GET` | Kitoblar, mualliflar va kitobxonlar bo'yicha tezkor qidiruv va filtr. |
| **`app/u/[okjId]/page.tsx`** | Demo kitobxon profili va pasport darajalari | `/api/v1/passport/{okjId}/` | `GET` | Foydalanuvchining elektron pasporti, muhrlari (stamps) va XP darajasi. |
| **`app/notifications/page.tsx`** | Hardcode `notifications` array (4 ta xabar) | `/api/v1/notifications/` | `GET` | O'qilmagan xabarlar ro'yxati va ularni o'qilgan deb belgilash (`PATCH`). |
| **`app/settings/page.tsx`** | `useState({ firstName: 'Alisher'... })` | `/api/v1/users/me/` | `GET` / `PATCH` | Foydalanuvchi ma'lumotlarini o'qish, profil rasm va bio ni tahrirlash. |
| **`components/features/post-detail/*`** | Fallback fikrlar va o'xshash kitoblar ro'yxati | `/api/v1/books/{slug}/related/` | `GET` | O'xshash asarlar va mavzuga doir postlar integratsiyasi. |

---

## 🔒 2. Integratsiya Qoidalari

1. **Hech qanday UI / UX buzilmaydi:** Apple VisionOS, Instagram Feed, Goodreads va Duolingo Glass Design System aynan saqlanib qoladi.
2. **Error Handling normalization:** Har bir endpoint xatolik berganda `<GlassErrorState />` yoki API Error Toast orqali ko'rsatiladi.
3. **Optimistic Updates:** Like, Bookmark, Follow va Comment qo'shish jarayonlari 0 ms ichida ekranda aks etadi va fonda serverga yoziladi.
