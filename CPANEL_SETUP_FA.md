# TiTaN × Dark Pulse — سیستم هبريدی سلف بات برای cPanel

این بسته یک سیستم **هбриدی** است که بهترین ویژگی‌های دو نسخه را combining می‌کند:

| بخش | کدام نسخه | توضیح |
|------|----------|-------|
| **ربات اصلی (bot.py)** | **Dark Pulse (botself.py)** | سیستم خرید اشتراک، فعال‌سازی سلف، کیف پول، کد هدیه، پنل مدیریت ادمین، لاگین کد 5 رقمی، استخراج self.py از Self.zip |
| **ربات کمکی/پنل (helper.py)** | **TiTaN SelfSaz** | کارت دیجیتال تیتان (رندر عکس + دکمه‌های زیر تصویر)، پنل اینلاین ۲۴ بخش، افکت عکس، منشی، دانلودر، آپلودر، AI، و ... |

> **ساختار خرید و فعالسازی سلف دقیقاً همان botself.py است** — هیچ تغییری در آن ایجاد نشده است.

---

## فایل‌های بسته

| فایل | توضیح |
|------|-------|
| `bot.py` | ربات اصلی — سیستم فروش و فعالسازی سلف (Dark Pulse) |
| `helper.py` | ربات کمکی — پنل و قابلیت‌های TiTaN |
| `source/Self.zip` | فایل سلف کاربر (در هنگام فعال‌سازی استخراج می‌شود) |
| `source/assets/titan_card_template.png` | تمپلیت کارت دیجیتال تیتان (قرمزه) |
| `source/fonts/` | فونت‌های Orbitron, Rajdhani, Vazirmatn (برای رندر کارت) |
| `pips1.txt`, `pips2.txt`, `pips3.txt` | کتابخانه‌های مورد نیاز |
| `CPANEL_SETUP_FA.md` | این راهنما |

---

## ۱) پیش‌نیازها

1. Linux و Python 3.10 یا بالاتر (سرور شما 3.12 است)
2. MySQL / MariaDB و دسترسی نوشتن در دیتابیس
3. اتصال خروجی به Telegram
4. cPanel اشتراکی: Cron هر دقیقه و اجازهٔ اجرای پردازش پایتون
5. `ffmpeg` و `mediainfo` (اختیاری؛ برای برخی قابلیت‌های مدیا)

---

## ۲) آپلود فایل‌ها

تمام فایل‌ها را در مسیر سرور خود آپلود کنید:

```
/home/vsnuklf/selfbot/selfbot/
```

ساختار نهایی باید اینگونه باشد:

```
/home/vsnuklf/selfbot/selfbot/
├── bot.py
├── helper.py
├── pips1.txt
├── pips2.txt
├── pips3.txt
├── CPANEL_SETUP_FA.md
└── source/
    ├── Self.zip
    ├── assets/
    │   └── titan_card_template.png
    └── fonts/
        ├── Orbitron/
        ├── Rajdhani/
        └── Vazirmatn/
```

> **مهم:** پوشه `source/` و محتوای آن باید دقیقاً در کنار `bot.py` و `helper.py` باشد. در غیر این صورت:
> - کارت دیجیتال تیتان با تمپلیت پیش‌فرض (نه عکس قرمزه) نمایش داده می‌شود
> - فعال‌سازی سلف کاربر با خطا مواجه می‌شود (Self.zip پیدا نمی‌شود)

---

## ۳) ساخت دیتابیس

در cPanel بخش **MySQL Databases**:
1. یک دیتابیس بسازید (مثلاً `vsnuklf_selfbot`)
2. یک کاربر دیتابیس بسازید و رمز قوی تعیین کنید
3. کاربر را به دیتابیس اضافه کنید و **ALL PRIVILEGES** بدهید
4. نام کامل دیتابیس، کاربر، رمز، میزبان (معمولاً `localhost`) و پورت (معمولاً `3306`) را یادداشت کنید

جداول زیر در اولین اجرا به صورت **خودکار** ساخته می‌شوند:
- `user` — کاربران (id, step, phone, amount, expir, account, self, pid)
- `gift_codes` — کدهای هدیه
- `used_gift_codes` — کدهای استفاده شده
- `bot` — وضعیت ربات (ON/OFF)
- `block` — کاربران مسدود شده
- `ownerlist` — لیست مالکان (در دیتابیس هلپر)
- `adminlist` — لیست ادمین‌ها (در دیتابیس هلپر)

---

## ۴) تنظیمات در فایل‌های Python (بدون `.env`)

تنظیمات را مستقیماً در ابتدای هر فایل قرار دهید.

### در `bot.py` — بخش Config (Dark Pulse)

```python
Admin = 123456789          # ایدی عددی شما (مدیر ربات)
Token = "123456:ABC-DEF..." # توکن ربات اصلی از BotFather
API_ID = 123456            # از my.telegram.org
API_HASH = "abcdef1234567890..." # از my.telegram.org
Channel_ID = "yourchannel"  # یوزرنیم کانال عضوگیری اجباری (بدون @)
Helper_ID = "helper_bot"    # یوزرنیم ربات هلپر (بدون @)
DBName = "vsnuklf_selfbot"  # نام دیتابیس اصلی
DBUser = "vsnuklf_user"     # کاربر دیتابیس اصلی
DBPass = "your_password"    # رمز دیتابیس اصلی
HelperDBName = "vsnuklf_selfbot"  # دیتابیس هلپر (می‌تواند همان باشد)
HelperDBUser = "vsnuklf_user"     # کاربر دیتابیس هلپر
HelperDBPass = "your_password"    # رمز دیتابیس هلپر
CardNumber = "1234567890123456"  # شماره کارت برای پرداخت
CardName = "نام کامل صاحب کارت"   # نام صاحب کارت
```

### در `helper.py` — بخش LOCAL CONFIGURATION (TiTaN)

```python
LOCAL_CONFIG = {
    "ADMIN_ID": 123456789,        # همان ایدی عددی مدیر
    "API_ID": 123456,             # همان API_ID
    "API_HASH": "abcdef1234567890...", # همان API_HASH
    "BOT_TOKEN": "123456:ABC-DEF...",  # توکن ربات اصلی (فقط fallback)
    "HELPER_BOT_TOKEN": "123456:GHI-JKL...", # توکن ربات کمکی/هلپر از BotFather
    "DATABASE_URL": "",
    "MYSQLHOST": "localhost",
    "MYSQLPORT": 3306,
    "MYSQLDATABASE": "vsnuklf_selfbot",  # همان دیتابیس bot.py
    "MYSQLUSER": "vsnuklf_user",    # همان کاربر دیتابیس
    "MYSQLPASSWORD": "your_password", # همان رمز دیتابیس
}
```

> **توجه:** مقادیر API و دیتابیس در هر دو فایل باید **یکسان** باشند تا هر دو ربات به یک دیتابیس دسترسی داشته باشند.

---

## ۵) نصب کتابخانه‌ها

در ترمینال cPanel یا SSH:

```bash
cd /home/vsnuklf/selfbot/selfbot
source /home/vsnuklf/virtualenv/selfbot/3.12/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r pips1.txt
pip install -r pips2.txt
pip install -r pips3.txt
```

---

## ۶) ایجاد دایرکتوری‌ها و مجوزها

```bash
mkdir -p sessions selfs source logs
chmod -R 777 sessions selfs
chmod 644 bot.py helper.py
chmod -R 755 source/
```

---

## ۷) اجرای دستی برای تست

ترمینال اول — ربات اصلی:
```bash
source /home/vsnuklf/virtualenv/selfbot/3.12/bin/activate
cd /home/vsnuklf/selfbot/selfbot
python bot.py
```

ترمینال دوم — ربات کمکی:
```bash
source /home/vsnuklf/virtualenv/selfbot/3.12/bin/activate
cd /home/vsnuklf/selfbot/selfbot
python helper.py
```

اگر هر دو بدون خطا اجرا شدند و به MySQL متصل شدند،Setup درست است.

---

## ۸) اجرای دائم با کرون جاب

در cPanel → **Cron Jobs**، هر دقیقه یکبار اجرا کنید:

```text
* * * * * cd /home/vsnuklf/selfbot/selfbot && source /home/vsnuklf/virtualenv/selfbot/3.12/bin/activate && python bot.py > /home/vsnuklf/selfbot/selfbot/logs/bot.log 2>&1
```

```text
* * * * * cd /home/vsnuklf/selfbot/selfbot && source /home/vsnuklf/virtualenv/selfbot/3.12/bin/activate && python helper.py > /home/vsnuklf/selfbot/selfbot/logs/helper.log 2>&1
```

> قبل از ست کردن کرون، مطمئن شوید هر دو ربات به صورت دستی اجرا شده و خطایی ندارند.

---

## ۹) چگونه سیستم کار می‌کند

### برای کاربر عادی:
1. `/start` → نمایش منوی اصلی (حساب کاربری، خرید اشتراک، قیمت، کیف پول، احراز هویت، اطلاعات اشتراک، کد هدیه، سلف چیست؟، پشتیبانی)
2. خرید اشتراک → انتخابduration (1-6 ماهه) → لاگین با شماره تلفن و کد 5 رقمی → استخراج self.py از Self.zip → فعال‌سازی سلف با subprocess
3. کیف پول → افزایش موجودی (فاکتور با شماره کارت)، انتقال موجودی، استفاده از کد هدیه
4. احراز هویت → ارسال عکس کارت برای تایید توسط مدیر

### برای مدیر (Admin):
پنل Reply Keyboard با امکانات:
- آمار 📊
- ارسال همگانی / فوروارد همگانی
- بلاک / آنبلاک کاربر
- افزایش / کسر موجودی
- افزایش / کسر زمان اشتراک
- فعال / غیرفعال کردن سلف کاربر
- روشن / خاموش کردن ربات
- مدیریت کدهای هدیه
- ریست سلف کاربران
- حذف کامل سلف کاربر

### برای ربات کمکی (helper):
pénel اینلاین TiTaN با ۲۴ بخش (سراسری، پروفایل، دانلودر، آپلودر، حالت متن، حالت اکشن، وبهوک، قفل‌ها، کرون جاب، آنتی لاگین، تبچی، ویرایشگر عکس، گیف و لوگو، کامپایلر، ابزارها، اکانت، کتاب، سرگرمی، بازار، استیکر و گیف، هوش مصنوعی، عکس، موزیک، تنظیمات سیستم)

---

## ۱۰) نکات مهم

- **بagens تغییر در bot.py ایجاد نشده است** — سیستم خرید و فعالسازی دقیقاً همان botself.py از گیت‌هاب شما است.
- **کارت دیجیتال تیتان** فقط در helper.py render می‌شود و عکس کاربری را روی تمپلیت قرمزه قرار می‌دهد.
- هر دو ربات به **یک دیتابیس** متصل می‌شوند و جدول `user` را به اشتراک می‌گذارند.
- توکن، API_ID/Hash و رمز دیتابیس را در فایل عمومی نگذارید.
- برای فعال‌سازی سلف کاربر، فایل `source/Self.zip` باید در همان پوشه باشد.

اگر در هر مرحله اجرا یا تنظیم دیتابیس مشکل داشتید، خطای ترمینال را بفرستید تا رفع شود.