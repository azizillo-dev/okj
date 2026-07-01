# OKJ Platform - Feed Ranking Moduli Arxitekturasi (architecture.md)

Bu hujjat **Feed Ranking** modulining dizayn qarorlari, OKJ-ID numerical sorting arxitekturasi,
Time-Decay algoritmi, Fan-out on Write strategiyasi va barcha me'moriy tanlovlarni batafsil tushuntiradi.

---

## 1. Modulning Maqsadi va O'rnati

`feed_ranking` moduli OKJ platformasidagi kitobxonlar uchun algoritmik saralangan shaxsiy lenta
(Home Feed) yaratadi. Mavjud `posts`, `follows`, `interactions`, `comments` modullari ustida
**qatlam (layer)** sifatida ishlaydi — ularning jadvallarini yoki ichki kodlarini **o'zgartirmaydi**.

```
┌─────────────────────────────────────────────────┐
│              Feed Ranking Module                 │
│  services.py │ selectors.py │ apis.py │ tasks.py │
└─────────────────────┬───────────────────────────┘
                      │ o'qish faqat
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
  posts app      follows app    interactions app
```

---

## 2. OKJ-ID Numerical Sorting Muammosi va Yechimi

### Muammo: Lexicographical Sort

Eski arxitekturada `okj_id` faqat **matn (CharField)** sifatida saqlanardi:

```
'OKJ-9' > 'OKJ-10' > 'OKJ-100' > 'OKJ-1000' (matnli tartib: NOTO'G'RI!)
```

99,999 dan oshganda:
```
order_by("-okj_id") natijalari:
  OKJ-99999
  OKJ-9999
  OKJ-999
  OKJ-100000  ← TO'G'RI POZITSIYA EMAS!
```

### Yechim: `okj_number = PositiveIntegerField`

```python
okj_number = models.PositiveIntegerField(unique=True, null=True, db_index=True)
```

| Maydon | Tur | Maqsad |
|--------|-----|--------|
| `okj_id` | CharField | Inson o'qiydigan format: `"OKJ-10492"` |
| `okj_number` | PositiveIntegerField | Numerik saralash: `10492` (INTEGER) |

```python
# To'g'ri:
User.all_objects.order_by("-okj_number").first()  # 100000 > 99999 ✓

# Noto'g'ri (eski):
User.all_objects.order_by("-okj_id").first()       # '99999' > '100000' ✗
```

---

## 3. OKJ-ID Race Condition Yechimi (Row-Level Lock)

### Muammo: TOCTOU (Time of Check, Time of Use)

```python
# XAVFLI (eski kod):
last_id = User.all_objects.count() + 10001
# ← Bu yerda boshqa so'rov ham bir xil count() olishi mumkin!
okj_id = f"OKJ-{last_id}"
```

Ikki so'rov ayni vaqtda: ikkisi ham `count() = 5000` ko'radi → ikkisi ham `OKJ-15001` oladi → **Duplicate!**

### Yechim: PostgreSQL Row-Level Lock

```python
@classmethod
@transaction.atomic
def _generate_atomic_okj_id(cls) -> tuple[int, str]:
    last_user = (
        User.all_objects
        .filter(okj_number__isnull=False)
        .order_by("-okj_number")
        .select_for_update()   # ← FOR UPDATE lock
        .first()
    )
    next_number = (last_user.okj_number + 1) if last_user else OKJ_NUMBER_START
    return next_number, f"OKJ-{next_number}"
```

`SELECT ... FOR UPDATE` PostgreSQL da qatorni qullab qo'yadi.
Ikkinchi so'rov birinchi tranzaksiya tugamaguncha **kutadi** — takrorlanmas ID kafolatlanadi.

```
T1: SELECT max → 10001 → LOCK   T2: SELECT max → WAIT...
T1: INSERT user(okj_number=10001)
T1: COMMIT → UNLOCK
                                 T2: SELECT max → 10001 → 10002
                                 T2: INSERT user(okj_number=10002)
```

---

## 4. Time-Decay Reyting Algoritmi

$$\text{Score} = \frac{\text{Base\_Weight} + (\text{Likes} \times 10) + (\text{Comments} \times 20)}{(\text{Age\_In\_Hours} + 2)^{1.5}}$$

### Konstantalar:

| Post Turi | Base_Weight | Sabab |
|-----------|-------------|-------|
| REVIEW, EXCHANGE, SELL, GIFT | **50** | Platformaning asosiy qadriyati — chuqur taqrizlar va real kitob almashinish |
| QUOTE, SHOWCASE | **20** | Ijodiy kontent — qimmatli lekin kam munozarali |
| Boshqalar | **10** | Umum postlar |

### Engagement Multiplikatorlar:
- **Likes × 10**: Har bir layk 10 ball beradi
- **Comments × 20**: Izohlar laykdan 2x qadrli — real muloqot ko'rsatkichi

### Time-Decay:
- `+2` denominator ichida: Yangi post (0 soatlik) cheksizlikka bo'linib ketmaydi
- `^1.5` (gravity): Eksponentsial pasayish — eski postlar vaqt o'tishi bilan pastga tushadi

---

## 5. Feed Arxitektura Strategiyalari

### 5.1. Fan-in (Pull) — `generate_user_feed_cache`

```
[Cache Miss / Kesh eski] → DB Query (Following posts 30 kun) → Score hisoblash → Redis ZSET
```

- Kesh muddati tugaganda yoki yangi foydalanuvchi uchun
- PostgreSQL'dan bir to'plamda o'qiydi (N+1 yo'q: `annotate` orqali)

### 5.2. Fan-out on Write — `fan_out_new_post`

```
[Yangi post] → Score hisoblash → Barcha obunachilar uchun ZADD
```

- Yozish paytida push (post yaratilganda)
- Faqat keshi mavjud obunachilar uchun (isrof qilinmaydi)
- **Celebrity Problem**: Celery asinxron task orqali bajariladi

### 5.3. Fail-Safe Fallback

```
[Redis xatosi] → SQL Fallback → PostgreSQL (select_related + prefetch_related)
```

- Tizim hech qachon yiqilmaydi
- Celery task fon rejimida keshni tiklaydi

---

## 6. Request Flow (So'rovlar Oqimi)

```
GET /api/v1/posts/feed/?page=1
        │
        ▼
UserRankedFeedApi (Thin View)
        │
        ▼
FeedRankingSelector.get_ranked_feed_for_user(user, page=1)
        │
        ├── Redis ZREVRANGE("user:feed:cache:<user_id>", 0, 19)
        │       │
        │       ├── [Cache Hit] → Post IDs → DB batch query → Return
        │       │
        │       └── [Cache Miss / Redis Error]
        │               │
        │               ├── Celery: rebuild_user_feed_cache_task.delay(user_id)
        │               └── SQL Fallback → PostQuerySet → Return
        │
        ▼
PostReadSerializer (many=True)
        │
        ▼
200 OK { success: true, data: { count, next, previous, results } }
```

---

## 7. Indekslar va Optimization Qarorlari

### accounts.User:

| Indeks | Sabab |
|--------|-------|
| `okj_number` (db_index) | `order_by("-okj_number")` tezkor — O(log N) |
| `okj_id` (db_index) | Pasport ID bo'yicha tezkor qidiruv |

### feed_ranking (Redis):

| Key Pattern | Tuzilma | TTL |
|-------------|---------|-----|
| `user:feed:cache:<user_id>` | ZSET (score → post_id) | 3600 s |

### PostgreSQL Optimization:

```python
# N+1 muammosiz — 1 query barcha ma'lumotlar uchun
Post.published_objects.filter(id__in=post_ids)
    .select_related("user", "book", "district")
    .prefetch_related("media")
```

---

## 8. Kelajakdagi Masshtablash Rejasi

| Masshtab | Muammo | Yechim |
|----------|--------|--------|
| 10K DAU | Asosiy arxitektura yetarli | Hozirgi kod |
| 100K DAU | Redis memory | Redis Cluster, top 200 ga cheklash |
| 1M DAU | Celebrity fan-out (10M+ obunachilar) | Hybrid: Celebrity → Pull, oddiy → Push |
| 10M DAU | PostgreSQL bottleneck | Cassandra/ScyllaDB feed storage |

### Celebrity Problem Yechimi (1M+ da):

```python
CELEBRITY_FOLLOWER_THRESHOLD = 10_000

if author.followers_count > CELEBRITY_FOLLOWER_THRESHOLD:
    # Pull strategiyasi: Obunachining so'rovida real-time qo'shiladi
    pass
else:
    # Push strategiyasi: Fan-out (hozirgi yondashuv)
    fan_out_post_to_followers_task.delay(post_id, author_id)
```
