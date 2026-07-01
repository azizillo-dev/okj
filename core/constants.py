"""
OKJ PLATFORM - SYSTEM CONSTANTS (core/constants.py)
Nega bu fayl kerak: Barcha chegirma limitlari, XP miqdorlari va kash vaqtlarini
yagona joyda saqlash.
"""

# Gamification XP Constants
XP_FOR_DAILY_CHECKIN = 10
XP_FOR_NEW_REVIEW = 30
XP_FOR_EXCHANGE_COMPLETE = 50

# Caching timeouts (seconds)
CACHE_TIMEOUT_FEED = 300       # 5 daqiqa
CACHE_TIMEOUT_BOOKS = 3600     # 1 soat
CACHE_TIMEOUT_DISTRICTS = 86400 # 24 soat (hududlar deyarli o'zgarmaydi)

# Upload limits
MAX_IMAGE_UPLOAD_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
