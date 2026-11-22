# TiTaN × Dark Pulse — سیستم هبریدی سلف بات (نسخه تصحیح شده)

این نسخه **کاملاً بر اساس Dark Pulse (botself.py)** است و هیچ تغییری در سیستم خرید، فعال‌سازی، کیف پول و پنل مدیریت ایجاد نشده است. فقط قابلیت **کارت دیجیتال تیتان** به ربات کمکی (helper) اضافه شده است.

## فایل‌های بسته

| فایل | توضیح |
|------|-------|
| `bot.py` | ربات اصلی — دقیقاً همان `botself.py` از گیت‌هاب Dark Pulse (بدون هیچ تغییری) |
| `helper.py` | ربات کمکی — بر اساس Dark Pulse helper.py + کارت دیجیتال تیتان |
| `source/Self.zip` | فایل سلف کاربر (در هنگام فعال‌سازی استخراج می‌شود) |
| `source/assets/titan_card_template.png` | تمپلیت کارت دیجیتال تیتان (قرمزه) |
| `source/fonts/` | فونت‌های Orbitron, Rajdhani, Vazirmatn |
| `pips1.txt`, `pips2.txt`, `pips3.txt` | کتابخانه‌های مورد نیاز |
| `CPANEL_SETUP_FA.md` | این راهنما |

---

## ۱) پیش‌نیازها

1. Linux و Python 3.10 یا بالاتر (سرور شما 3.12 است)
2. MySQL / MariaDB و دسترسی نوشتن در دیتابیس
3. اتصال خروجی به Telegram
4. cPanel اشتراکی: Cron هر دقیقه و اجازهٔ اجرای پردازش پایتون

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

> **مهم:** پوشه `source/` و محتوای آن باید دقیقاً در کنار `bot.py` و `helper.py` باشد. در غیر این صورت کارت دیجیتال تیتان نمایش داده نمی‌شود و فعال‌سازی سلف کاربر با خطا مواجه می‌شود.

---

## ۳) ساخت دیتابیس

در cPanel بخش **MySQL Databases**:
1. یک دیتابیس بسازید (مثلاً `vsnuklf_selfbot`)
2. یک کاربر دیتابیس بسازید و رمز قوی تعیین کنید
3. کاربر را به دیتابیس اضافه کنید و **ALL PRIVILEGES** بدهید
4. نام کامل دیتابیس، کاربر، رمز، میزبان (معمولاً `localhost`) و پورت (معمولاً `3306`) را یادداشت کنید

جداول زیر در اولین اجرا به صورت **خودکار** ساخته می‌شوند:
- `user` — کاربران (id, step)
- `ownerlist` — لیست مالکان
- `adminlist` — لیست ادمین‌ها

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

### در `helper.py` — بخش Config (Dark Pulse + تیتان)

```python
owner = 123456789   # ایدی عددی مدیر (همان Admin در bot.py)
api_id = 123456     # همان API_ID
api_hash = "abcdef1234567890..."  # همان API_HASH
bot_token = "123456:GHI-JKL..."  # توکن ربات کمکی/هلپر از BotFather
DBName = "vsnuklf_selfbot"  # همان دیتابیس bot.py
DBUser = "vsnuklf_user"     # همان کاربر دیتابیس
DBPass = "your_password"    # همان رمز دیتابیس
```

> **توجه:** مقادیر API و دیتابیس در هر دو فایل باید **یکسان** باشند تا هر دو ربات به یک دیتابیس دسترسی داشته باشند.

---

## ۵) نصب کتابخانه‌ها

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
mkdir -p sessions selfs source logs panel_cache/cards
chmod -R 777 sessions selfs panel_cache
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

### برای کاربر عادی (در helper):
- `/start` — پیام خوش آمدگویی با دکمه Panel
- `/panel` — باز کردن پنل همراه با **کارت دیجیتال تیتان** (عکس پروفایل کاربر + اطلاعات + دکمه‌های پنل زیر تصویر)
- دکمه‌های پنل شامل ۲۴ بخش (سراسری، پروفایل، دانلودر، آپلودر، حالت متن، حالت اکشن، وبهوک، قفل‌ها، کرون جاب، آنتی لاگین، تبچی، ویرایشگر عکس، گیف و لوگو، کامپایلر، ابزارها، اکانت، کتاب، سرگرمی، بازار، استیکر و گیف، هوش مصنوعی، عکس، موزیک، تنظیمات سیستم)

### برای مدیر (در bot.py):
پنل Reply Keyboard با امکانات:
- آمار، ارسال همگانی، بلاک/آنبلاک، افزایش/کسر موجودی و زمان، فعال/غیرفعال سلف، روشن/خاموش ربات، مدیریت کدهای هدیه

---

## ۱۰) نکات مهم

- **bot.py هیچ تغییری نداشته است** — دقیقاً همان botself.py از گیت‌هاب Dark Pulse است.
- **جوین اجباری (.monshi2) در helper.py حفظ شده است** (در بخش قفل‌ها).
- **کارت دیجیتال تیتان** وقتی `/panel` زده می‌شود، عکس کارت همراه با دکمه‌های پنل نمایش داده می‌شود (عکس حذف نمی‌شود).
- هر دو ربات به **یک دیتابیس** متصل می‌شوند.
- توکن، API_ID/Hash و رمز دیتابیس را در فایل عمومی نگذارید.
- برای فعال‌سازی سلف کاربر، فایل `source/Self.zip` باید در همان پوشه باشد.

اگر در هر مرحله اجرا یا تنظیم دیتابیس مشکل داشتید، خطای ترمینال را بفرستید تا رفع شود.