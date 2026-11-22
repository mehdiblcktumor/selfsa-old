#============ In The Name Of God ============#
# Source Name: Ultra Self Creator
# Source Version: 1.4.3
# Channel: Fadelta_source
# TiTaN Digital Card + Dark Pulse Structure Integration
#================== Import ==================#
from pyrogram import Client, filters, idle, errors
from pyrogram.types import *
from pyrogram.raw import functions, base, types
from colorama import Fore
import requests
import pymysql
import json
import sys
import os
import asyncio
import hashlib
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

#================= Dark Pulse Config =================#
owner = 0          # ایدی عددی مدیر (مقدار واقعی قرار دهید)
api_id = 0         # API ID
api_hash = "0"     # API HASH
bot_token = "0"    # توکن ربات کمکی/هلپر
DBName = "0"       # نام دیتابیس
DBUser = "0"       # کاربر دیتابیس
DBPass = "0"       # رمز دیتابیس
#==========================================#

#================= TiTaN Digital Card Assets =================#
BASE_DIR = Path(__file__).resolve().parent
TITAN_SOURCE_DIR = BASE_DIR / "source"
TITAN_ASSETS_DIR = TITAN_SOURCE_DIR / "assets"
TITAN_FONTS_DIR = TITAN_SOURCE_DIR / "fonts"

TITAN_TEMPLATE_PATH = None
TITAN_FONT_PATHS = {}

def _titan_find_template():
    """Find the Titan card template image (Dark Pulse structure, Titan asset)."""
    preferred = (
        "titan_card_template.png",
        "titan_card_template.jpg",
        "titan_card_template.jpeg",
    )
    for name in preferred:
        candidate = TITAN_ASSETS_DIR / name
        if candidate.is_file():
            return candidate
    if TITAN_ASSETS_DIR.is_dir():
        image_files = sorted(
            p for p in TITAN_ASSETS_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        )
        if image_files:
            return image_files[0]
    return None

def _titan_find_font(folder, preferred_names, keywords=()):
    """Find a TTF font by preferred name first, then by useful filename keywords."""
    folder = Path(folder)
    if folder.is_dir():
        files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".ttf")
    else:
        files = []
    if not files:
        files = sorted(p for p in TITAN_FONTS_DIR.rglob("*.ttf") if p.is_file()) if TITAN_FONTS_DIR.is_dir() else []
    if not files:
        return None
    by_lower = {p.name.lower(): p for p in files}
    for name in preferred_names:
        if name.lower() in by_lower:
            return by_lower[name.lower()]
    for p in files:
        low = p.name.lower()
        if all(keyword.lower() in low for keyword in keywords):
            return p
    if len(files) == 1:
        return files[0]
    return files[0]

def _titan_load_fonts():
    """Load Titan card fonts."""
    global TITAN_FONT_PATHS
    fonts = {}
    font_specs = {
        "orbitron_black": (TITAN_FONTS_DIR / "Orbitron", ("Orbitron-Black.ttf", "Orbitron-ExtraBold.ttf", "Orbitron-Bold.ttf"), ("orbitron", "black")),
        "orbitron_medium": (TITAN_FONTS_DIR / "Orbitron", ("Orbitron-Medium.ttf", "Orbitron-Regular.ttf", "Orbitron.ttf"), ("orbitron", "medium")),
        "rajdhani_semibold": (TITAN_FONTS_DIR / "Rajdhani", ("Rajdhani-SemiBold.ttf", "Rajdhani-Bold.ttf", "Rajdhani-Medium.ttf"), ("rajdhani", "semibold")),
        "rajdhani_medium": (TITAN_FONTS_DIR / "Rajdhani", ("Rajdhani-Medium.ttf", "Rajdhani-Regular.ttf", "Rajdhani-SemiBold.ttf"), ("rajdhani", "medium")),
        "vazirmatn_semibold": (TITAN_FONTS_DIR / "Vazirmatn", ("Vazirmatn-SemiBold.ttf", "Vazirmatn-Bold.ttf", "Vazirmatn-Medium.ttf", "Vazirmatn-Regular.ttf"), ("vazirmatn", "semibold")),
    }
    for key, (folder, names, keywords) in font_specs.items():
        fpath = _titan_find_font(folder, names, keywords)
        if fpath and fpath.is_file():
            fonts[key] = fpath
    return fonts

TITAN_NATIVE_SIZE = (1280, 853)
TITAN_PROFILE_POLYGON = (
    (104, 228), (185, 149), (329, 149), (412, 229),
    (412, 389), (329, 469), (185, 469), (104, 389),
)
TITAN_TEXT_AREAS = {
    "name": (766, 255, 992, 303),
    "id": (766, 331, 992, 379),
    "username": (766, 408, 992, 456),
    "status": (766, 484, 992, 532),
}
TITAN_TEXT_COLOR = (245, 245, 245, 255)

def _titan_font(path, size):
    return ImageFont.truetype(str(path), int(size))

def _titan_contains_rtl(text):
    return any(
        ("\u0600" <= ch <= "\u06ff") or ("\u0750" <= ch <= "\u077f")
        for ch in str(text or "")
    )

def fit_text_to_area(draw, text, area, font_path, max_size=28, min_size=13, direction=None):
    left, top, right, bottom = area
    max_width = max(1, right - left)
    max_height = max(1, bottom - top)
    clean_text = str(text or "").strip() or "—"
    for size in range(int(max_size), int(min_size) - 1, -1):
        font = _titan_font(font_path, size)
        bbox = draw.textbbox((0, 0), clean_text, font=font)
        if (bbox[2] - bbox[0]) <= max_width and (bbox[3] - bbox[1]) <= max_height:
            return font, clean_text
    ellipsis = "…"
    candidate = clean_text
    while len(candidate) > 1:
        candidate = candidate[:-1].rstrip()
        shortened = candidate + ellipsis
        font = _titan_font(font_path, min_size)
        bbox = draw.textbbox((0, 0), shortened, font=font)
        if (bbox[2] - bbox[0]) <= max_width and (bbox[3] - bbox[1]) <= max_height:
            return font, shortened
    return _titan_font(font_path, min_size), ellipsis

def draw_titan_text(draw, text, area, font_path, max_size=28, min_size=13, direction=None):
    left, top, right, bottom = area
    font, fitted_text = fit_text_to_area(draw, text, area, font_path, max_size=max_size, min_size=min_size, direction=direction)
    center_y = (top + bottom) // 2
    if direction == "rtl":
        try:
            draw.text((right, center_y), fitted_text, font=font, fill=TITAN_TEXT_COLOR, anchor="rm", direction="rtl", language="fa")
            return
        except Exception:
            pass
    draw.text((left, center_y), fitted_text, font=font, fill=TITAN_TEXT_COLOR, anchor="lm")

def _titan_status_text(user):
    status = getattr(user, "status", None)
    status_name = getattr(status, "__class__", type(status)).__name__.lower()
    status_map = {
        "userstatusonline": "ONLINE",
        "userstatusoffline": "OFFLINE",
        "userstatusrecently": "RECENTLY",
        "userstatuslastweek": "LAST WEEK",
        "userstatuslastmonth": "LAST MONTH",
        "userstatusempty": "UNKNOWN",
    }
    return status_map.get(status_name, "UNKNOWN")

async def get_titan_profile_photo(client, user_id, user_obj=None):
    """Download the CURRENT user's real Telegram profile photo in memory."""
    try:
        chat_photo = getattr(user_obj, "photo", None) if user_obj else None
        file_id = (
            getattr(chat_photo, "big_file_id", None)
            or getattr(chat_photo, "small_file_id", None)
        )
        if file_id:
            downloaded = await client.download_media(file_id, in_memory=True)
            if downloaded:
                try:
                    downloaded.seek(0)
                except Exception:
                    pass
                downloaded.titan_cache_key = str(file_id)
                return downloaded
        try:
            tg_user = await client.get_users(int(user_id))
        except Exception:
            tg_user = None
        chat_photo = getattr(tg_user, "photo", None) if tg_user else None
        file_id = (
            getattr(chat_photo, "big_file_id", None)
            or getattr(chat_photo, "small_file_id", None)
        )
        if file_id:
            downloaded = await client.download_media(file_id, in_memory=True)
            if downloaded:
                try:
                    downloaded.seek(0)
                except Exception:
                    pass
                downloaded.titan_cache_key = str(file_id)
                return downloaded
        async for photo in client.get_chat_photos(int(user_id), limit=1):
            file_id = (
                getattr(photo, "file_id", None)
                or getattr(photo, "big_file_id", None)
                or getattr(photo, "small_file_id", None)
            )
            if file_id:
                downloaded = await client.download_media(file_id, in_memory=True)
                if downloaded:
                    try:
                        downloaded.seek(0)
                    except Exception:
                        pass
                    downloaded.titan_cache_key = str(file_id)
                    return downloaded
            break
        try:
            api_token = str(bot_token or "").strip()
            if api_token and api_token != "0":
                photos_res = requests.get(
                    f"https://api.telegram.org/bot{api_token}/getUserProfilePhotos",
                    params={"user_id": int(user_id), "limit": 1},
                    timeout=20
                ).json()
                if photos_res.get("ok") and photos_res.get("result", {}).get("photos"):
                    sizes = photos_res["result"]["photos"][0]
                    best = sizes[-1]
                    file_id = best.get("file_id")
                    if file_id:
                        file_res = requests.get(
                            f"https://api.telegram.org/bot{api_token}/getFile",
                            params={"file_id": file_id},
                            timeout=20
                        ).json()
                        file_path = file_res.get("result", {}).get("file_path") if file_res.get("ok") else None
                        if file_path:
                            content = requests.get(
                                f"https://api.telegram.org/file/bot{api_token}/{file_path}",
                                timeout=30
                            ).content
                            if content:
                                bio = BytesIO(content)
                                bio.name = "titan_profile_photo.jpg"
                                bio.seek(0)
                                bio.titan_cache_key = str(file_id)
                                return bio
        except Exception:
            pass
        return None
    except Exception:
        return None

def _titan_paste_profile_photo(card, photo_stream):
    """Fit the user's profile photo into the TiTaN octagon."""
    if photo_stream is None:
        return
    source = None
    should_close = False
    try:
        source = photo_stream
        if isinstance(photo_stream, (bytes, bytearray)):
            source = BytesIO(photo_stream)
        elif isinstance(photo_stream, (str, os.PathLike)):
            source = open(photo_stream, "rb")
            should_close = True
        else:
            try:
                source.seek(0)
            except Exception:
                pass
        with Image.open(source) as photo:
            photo = ImageOps.exif_transpose(photo)
            if photo.mode in ("RGBA", "LA") or (photo.mode == "P" and "transparency" in photo.info):
                rgba = photo.convert("RGBA")
                solid = Image.new("RGBA", rgba.size, (5, 5, 7, 255))
                solid.alpha_composite(rgba)
                photo = solid.convert("RGB")
            else:
                photo = photo.convert("RGB")
            inner_polygon = (
                (112, 226), (190, 150), (330, 150), (408, 228),
                (408, 391), (330, 468), (190, 468), (112, 391),
            )
            xs = [p[0] for p in inner_polygon]
            ys = [p[1] for p in inner_polygon]
            paste_box = (min(xs), min(ys), max(xs), max(ys))
            width = paste_box[2] - paste_box[0]
            height = paste_box[3] - paste_box[1]
            source_ratio = photo.width / max(1, photo.height)
            target_ratio = width / max(1, height)
            if source_ratio > target_ratio:
                crop_h = photo.height
                crop_w = int(crop_h * target_ratio)
                left = max(0, int((photo.width - crop_w) * 0.5))
                top = 0
            else:
                crop_w = photo.width
                crop_h = int(crop_w / target_ratio)
                left = 0
                focus_y = 0.34 if photo.height > photo.width else 0.5
                top = max(0, int((photo.height - crop_h) * focus_y))
            right = min(photo.width, left + crop_w)
            bottom = min(photo.height, top + crop_h)
            if right <= left or bottom <= top:
                cropped = ImageOps.fit(photo, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.42))
            else:
                cropped = photo.crop((left, top, right, bottom)).resize((width, height), Image.Resampling.LANCZOS)
            cropped = cropped.convert("RGBA")
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            polygon = [(x - paste_box[0], y - paste_box[1]) for x, y in inner_polygon]
            mask_draw.polygon(polygon, fill=255)
            layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
            layer.paste(cropped, paste_box[:2], mask)
            card.alpha_composite(layer)
        if should_close:
            try:
                source.close()
            except Exception:
                pass
    except Exception:
        pass

def generate_titan_user_card(user, profile_photo=None):
    """Render dynamic user data onto a fresh copy of the original Titan template."""
    if not TITAN_FONT_PATHS:
        _titan_load_fonts()
    template_path = _titan_find_template()
    if template_path is None:
        image = Image.new("RGB", TITAN_NATIVE_SIZE, (6, 12, 25))
        output = BytesIO()
        output.name = "titan_user_identity_card.png"
        image.save(output, format="PNG")
        output.seek(0)
        return output
    with Image.open(template_path) as source:
        source = ImageOps.exif_transpose(source).convert("RGBA")
        if source.size != TITAN_NATIVE_SIZE:
            source = source.resize(TITAN_NATIVE_SIZE, Image.Resampling.LANCZOS)
        card = source.copy()
    _titan_paste_profile_photo(card, profile_photo)
    draw = ImageDraw.Draw(card)
    first_name = (getattr(user, "first_name", None) or "").strip()
    last_name = (getattr(user, "last_name", None) or "").strip()
    display_name = " ".join(part for part in (first_name, last_name) if part).strip() or "Unknown"
    username = (getattr(user, "username", None) or "").strip().lstrip("@")
    username_text = f"@{username}" if username else "@NoUsername"
    user_id = str(getattr(user, "id", "") or "0")
    status_text = _titan_status_text(user)
    has_rtl_name = _titan_contains_rtl(display_name)
    draw_titan_text(
        draw, display_name, TITAN_TEXT_AREAS["name"],
        TITAN_FONT_PATHS.get("vazirmatn_semibold", TITAN_FONT_PATHS.get("rajdhani_semibold")),
        max_size=27, min_size=15,
        direction="rtl" if has_rtl_name else None,
    )
    draw_titan_text(
        draw, user_id, TITAN_TEXT_AREAS["id"],
        TITAN_FONT_PATHS.get("orbitron_medium", list(TITAN_FONT_PATHS.values())[0] if TITAN_FONT_PATHS else None),
        max_size=24, min_size=15,
    )
    draw_titan_text(
        draw, username_text, TITAN_TEXT_AREAS["username"],
        TITAN_FONT_PATHS.get("rajdhani_semibold", list(TITAN_FONT_PATHS.values())[0] if TITAN_FONT_PATHS else None),
        max_size=27, min_size=15,
    )
    draw_titan_text(
        draw, status_text, TITAN_TEXT_AREAS["status"],
        TITAN_FONT_PATHS.get("rajdhani_semibold", list(TITAN_FONT_PATHS.values())[0] if TITAN_FONT_PATHS else None),
        max_size=27, min_size=15,
    )
    output = BytesIO()
    output.name = "titan_user_identity_card.png"
    card.save(output, format="PNG", optimize=False, compress_level=0)
    output.seek(0)
    return output

#================= TiTaN Card Cache =================#
_titan_card_cache_dir = BASE_DIR / "panel_cache" / "cards"
_titan_card_cache_dir.mkdir(parents=True, exist_ok=True)

async def render_titan_user_card_cached(client, user):
    """Return a cached PNG file path for this user's current card."""
    uid = getattr(user, "id", 0)
    cache_path = _titan_card_cache_dir / f"titan_{uid}.png"
    if cache_path.is_file():
        return str(cache_path)
    profile_photo = await get_titan_profile_photo(client, user.id, user)
    titan_card = generate_titan_user_card(user, profile_photo)
    cache_path.write_bytes(titan_card.getvalue())
    return str(cache_path)

#================= Dark Pulse DB Functions =================#
def get_data(query):
     with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
          db = connect.cursor()
          db.execute(query)
          result = db.fetchone()
          return result

def get_datas(query):
     with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
          db = connect.cursor()
          db.execute(query)
          result = db.fetchall()
          return result

def update_data(query):
     with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
          db = connect.cursor()
          db.execute(query)
          connect.commit()

#================= Dark Pulse Tables =================#
update_data("""
CREATE TABLE IF NOT EXISTS user(
id bigint PRIMARY KEY,
step varchar(150) DEFAULT 'none'
) default charset=utf8mb4;
""")
update_data("""
CREATE TABLE IF NOT EXISTS ownerlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")
update_data("""
CREATE TABLE IF NOT EXISTS adminlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")

OwnerUser = get_data(f"SELECT * FROM ownerlist WHERE id = '{owner}' LIMIT 1")
if OwnerUser is None:
     update_data(f"INSERT INTO ownerlist(id) VALUES({owner})")

AdminUser = get_data(f"SELECT * FROM adminlist WHERE id = '{owner}' LIMIT 1")
if AdminUser is None:
     update_data(f"INSERT INTO adminlist(id) VALUES({owner})")

app = Client("Helper", api_id, api_hash, bot_token=bot_token)

#================= TiTaN Help Texts (All 24 Sections) =================#
# (Persian and English help texts for all Titan sections)
fahelp1 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
**[ سراسری - شخصی ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
سکوت کاربر
➤ [ `.mute` ]
———————————————
حذف سکوت کاربر
➤ [ `.unmute` ]
———————————————
پاکسازی لیست سکوت
➤ [ `.allunmute` ]
———————————————
بلاک کاربر
➤ [ `.block` ]
———————————————
آنبلاک کاربر
➤ [ `.unblock` ]
———————————————
افزودن کاربر به لیست دشمنان
➤ [ `.setenemy` ]
———————————————
حذف کاربر از لیست دشمنان
➤ [ `.delenemy` ]
———————————————
پاکسازی لیست دشمنان
➤ [ `.clearenemy` ]
———————————————
افزودن کاربر به لیست عشق
➤ [ `.setlove` ]
———————————————
حذف کاربر از لیست عشق
➤ [ `.dellove` ]
———————————————
پاکسازی لیست عشق
➤ [ `.clearlove` ]
———————————————
تنظیم متن منشی خودکار
➤ [ `.monshi` ] **⤳** (TEXT)
———————————————
غیرفعال کردن منشی خودکار
➤ [ `.monshioff` ]
———————————————
تنظیم متن حالت آفلاینی
➤ [ `.afk` ] **⤳** (TEXT)
———————————————
غیرفعال کردن حالت آفلاینی
➤ [ `.unafk` ]
———————————————
دریافت هشدار تگ شدن
➤ [ `.tagalert` ] **⤳** (on OR off)
———————————————
ساخت کانال
➤ [ `.creatchannel` ] **⤳** (Name)
———————————————
ساخت گروه
➤ [ `.creatgroup` ] **⤳** (Name)
———————————————
ساخت سوپر گروه
➤ [ `.creatsupergroup` ] **⤳** (Name)
———————————————
اسپم متن معمولی
➤ [ `.spam` ] **⤳** (NUM TEXT)
———————————————
اسپم متن آرام
➤ [ `.slowspam` ] **⤳** (NUM TEXT)
———————————————
اسپم متن و حذف
➤ [ `.statspam` ] **⤳** (NUM TEXT)
———————————————
اسپم متن سریع
➤ [ `.fastspam` ] **⤳** (NUM TEXT)
———————————————
فعال کردن کامنت اول
➤ [ `.firstcom` ] **⤳** (on OR off)
———————————————
تنظیم متن کامنت اول
➤ [ `.first_message` ] **⤳** (TEXT) (Reply)
———————————————
تنظیم زمان ارسال خودکار متن
➤ [ `.text_time` ] **⤳** (HH:MM)
———————————————
تنظیم زمان ارسال خودکار عکس
➤ [ `.photo_time` ] **⤳** (HH:MM)
———————————————
تنظیم متن ارسال خودکار متن
➤ [ `.text_send_time` ] **⤳** (TEXT) (Reply)
———————————————
تنظیم عکس ارسال خودکار عکس
➤ [ `.photo_send_time` ] **⤳** (Reply)
———————————————
فعال یا غیرفعال کردن پاسخ خودکار
➤ [ `.answer` ] **⤳** (on OR off)
———————————————
تنظیم سوال جواب برای پاسخ خودکار
➤ [ `.addan` ] **⤳** (Question:Answer)
———————————————
حذف یک سوال جواب
➤ [ `.delan` ] **⤳** (Answer)
———————————————
مشاهده لیست سوال جواب ها
➤ [ `.anlist` ]
———————————————
پاکسازی لیست پاسخ خودکار
➤ [ `.anclear` ]
———————————————
فعال یا غیرفعال کردن حالت خوش آمد گویی
➤ [ `.welcome` ] **⤳** (on OR off)
———————————————
تنظیم متن خوش آمد گویی
➤ [ `.welcome_add` ] **⤳** (TEXT)
———————————————
نمایش متن خوش آمد گویی
➤ [ `.welcome_show` ]
———————————————
ریست متن خوش آمد گویی
➤ [ `.welcome_reset` ]
———————————————
**توجه! برای استفاده از دستورات زیر باید مالک یا ادمین گروه مورد نظر با دسترسی های لازم باشید**

بن کاربر در گروه
➤ [ `.ban` ] **⤳** (ID) (Reply)
———————————————
آنبن کاربر در گروه
➤ [ `.unban` ] **⤳** (ID) (Reply)
———————————————
سکوت کاربر در گروه
➤ [ `.setmute` ] **⤳** (ID) (Reply)
———————————————
حذف سکوت کاربر در گروه
➤ [ `.delmute` ] **⤳** (ID) (Reply)
———————————————
تنظیم عکس گروه
➤ [ `.setchatphoto` ] **⤳** (Reply)
———————————————
تنظیم نام گروه
➤ [ `.setchattitle` ] **⤳** (TEXT)
———————————————
تنظیم بیوگرافی گروه
➤ [ `.setchatbio` ] **⤳** (TEXT)
———————————————
تنظیم نام کاربری گروه
➤ [ `.setchatusername` ] **⤳** (Username)
———————————————
سنجاق پیام در گروه
➤ [ `.pin` ] **⤳** (Reply)
———————————————
حذف سنجاق پیام در گروه
➤ [ `.unpin` ] **⤳** (Reply)
———————————————
حذف همه سنجاق های گروه
➤ [ `.unpinall` ]
———————————————
حذف کانال
➤ [ `.deletechannel` ] **⤳** (Username)
———————————————
حذف گروه
➤ [ `.deletegroup` ] **⤳** (Username)
———————————————
حذف همه پیام های کاربر در گروه
➤ [ `.delallmsguser` ] **⤳** (Reply)
———————————————
تنظیم زمان بین ارسال هر پیام برای اعضای گروه برحسب ثانیه
➤ [ `.slowmod` ] **⤳** (NUM)
———————————————
حذف تعدادی از پیام ها
➤ [ `.delete` ] **⤳** (NUM)
———————————————
تگ ادمین های گروه
➤ [ `.tadmin` ]
———————————————
تگ همه کاربران گروه
➤ [ `.tagall` ] **⤳** (TEXT) (Reply)
———————————————
لغو تگ کاربران گروه
➤ [ `.cancel` ]
———————————————
پاکسازی تاریخچه
➤ [ `.delethistory` ]
———————————————
حذف یک پیام
➤ [ `.del` ] **⤳** (Reply)
———————————————
"""

fahelp2 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ پروفایل ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
تنظیم نام اکانت
➤ [ `.setname` ] **⤳** (TEXT)
———————————————
تنظیم نام خانوادگی اکانت
➤ [ `.setlastname` ] **⤳** (TEXT)
———————————————
تنظیم بیوگرافی اکانت
➤ [ `.setbio` ] **⤳** (TEXT)
———————————————
تنظیم فونت خودکار نام
➤ [ `.fontname` ] **⤳** (on OR off)
———————————————
تنظیم ساعت روی نام
➤ [ `.timename` ] **⤳** (on OR off)
———————————————
تنظیم ساعت روی نام 2
➤ [ `.2timename` ] **⤳** (on OR off)
———————————————
تنظیم ساعت در بیوگرافی ساده
➤ [ `.timebio` ] **⤳** (on OR off)
———————————————
تنظیم ساعت در بیوگرافی رندوم
➤ [ `.2timebio` ] **⤳** (on OR off)
———————————————
تنظیم ساعت در بیوگرافی با خورشید و ماه
➤ [ `.3timebio` ] **⤳** (on OR off)
———————————————
تنظیم ساعت در بیوگرافی با خورشید و ماه و روز
➤ [ `.4timebio` ] **⤳** (on OR off)
———————————————
تنظیم ساعت در بیوگرافی با قلب رنگی
➤ [ `.5timebio` ] **⤳** (on OR off)
———————————————
تنظیم ساعت در بیوگرافی با ثبت فضولی
➤ [ `.6timebio` ] **⤳** (on OR off)
———————————————
تنظیم عکس پروفایل اکانت
➤ [ `.setprofile` ] **⤳** (Reply)
———————————————
حذف عکس پروفایل اکانت
➤ [ `.delprofile` ]
———————————————
تنظیم ساعت روی عکس پروفایل
➤ [ `.autopic` ]
———————————————
تنظیم ساعت روی عکس پروفایل 2
➤ [ `.2autopic` ]
———————————————
تنظیم ساعت روی عکس پروفایل 3
➤ [ `.3autopic` ]
———————————————
تنظیم ساعت روی عکس پروفایل 4
➤ [ `.4autopic` ]
———————————————
"""

fahelp3 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ دانلودر ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
دریافت اطلاعات پیج اینستاگرام
➤ [ `.iginfo` ] **⤳** (Username)
———————————————
دانلود از اینستاگرام
➤ [ `.igdl` ] **⤳** (URL)
———————————————
دانلود از اینستاگرام & یوتیوب &  فیسبوک & تیک تاک
➤ [ `.down` ] **⤳** (URL)
———————————————
جستجو و دانلود از یوتیوب با متن
➤ [ `.youtube` ] **⤳** (TEXT)
———————————————
جستجوی اپلیکیشن
➤ [ `.app` ] **⤳** (TEXT)
———————————————
جستجوی اپلیکیشن 2
➤ [ `.apk` ] **⤳** (TEXT)
———————————————
"""

fahelp4 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ آپلودر ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
آپلود متن
➤ [ `.neko` ] **⤳** (Reply)
———————————————
آپلود عکس
➤ [ `.telegraph` ] **⤳** (Reply)
———————————————
"""

fahelp5 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ حالت متن ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
حالت بولد
➤ [ `.bold` ] **⤳** (on OR off)
———————————————
حالت اسپویلر
➤ [ `.spoiler` ] **⤳** (on OR off)
———————————————
حالت کج نویس
➤ [ `.italic` ] **⤳** (on OR off)
———————————————
حالت کد نویس
➤ [ `.code` ] **⤳** (on OR off)
———————————————
حالت زیر خط
➤ [ `.underline` ] **⤳** (on OR off)
———————————————
حالت خط خوردگی
➤ [ `.strike` ] **⤳** (on OR off)
———————————————
حالت ایموجی
➤ [ `.emoji` ] **⤳** (on OR off)
———————————————
حالت نقل قول
➤ [ `.quote` ] **⤳** (on OR off)
———————————————
حالت منشن
➤ [ `.mention` ] **⤳** (on OR off)
———————————————
تنظیم ری اکشن روی کاربر
➤ [ `.setreact` ] **⤳** (Emoji) (Reply)
———————————————
حذف ری اکشن
➤ [ `.delreact` ] **⤳** (Reply)
———————————————
لیست ری اکشن ها
➤ [ `.reactlist` ]
———————————————
ارسال متن به صورت پله ای
➤ [ `.lad` ] **⤳** (TEXT)
———————————————
"""

fahelp6 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ حالت اکشن ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
حالت نوشتن
➤ [ `.typing` ] **⤳** (on OR off)
———————————————
حالت بازی کردن
➤ [ `.playing` ] **⤳** (on OR off)
———————————————
حالت ضبط ویدیو
➤ [ `.record_vid` ] **⤳** (on OR off)
———————————————
حالت انتخاب استیکر
➤ [ `.choose_sticker` ] **⤳** (on OR off)
———————————————
حالت آپلود ویدیو
➤ [ `.upload_vid` ] **⤳** (on OR off)
———————————————
حالت آپلود فایل
➤ [ `.upload_doc` ] **⤳** (on OR off)
———————————————
حالت آپلود فایل صوتی
➤ [ `.upload_audio` ] **⤳** (on OR off)
———————————————
حالت صحبت کردن
➤ [ `.speaking` ] **⤳** (on OR off)
———————————————
حالت آنلاین بودن اکانت
➤ [ `.online` ] **⤳** (on OR off)
———————————————
حالت آفلاین بودن اکانت
➤ [ `.offline` ] **⤳** (on OR off)
———————————————
"""

fahelp7 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ وبهوک ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
تنظیم وبهوک
➤ [ `.setwebhook` ] **⤳** (Token URL)
———————————————
حذف وبهوک
➤ [ `.delwebhook` ] **⤳** (Token)
———————————————
پاکسازی آپدیت های در انتظار
➤ [ `.delupdate` ] **⤳** (Token)
———————————————
دریافت اطلاعات وبهوک
➤ [ `.webhookinfo` ] **⤳** (Token)
———————————————
دریافت اطلاعات ربات
➤ [ `.botinfo` ] **⤳** (Token)
———————————————
"""

fahelp8 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ قفل ها ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
فعال یا غیرفعال کردن قفل پیوی
➤ [ `.pvlock` ] **⤳** (on OR off)
———————————————
فعال یا غیرفعال کردن جوین اجباری پیوی
➤ [ `.monshi2` ] **⤳** (on OR off)
———————————————
لیست نام قفل ها
➤ [ `.hlock` ]
———————————————
وضعیت قفل گروه
➤ [ `.locks` ]
———————————————
قفل یک ویژگی
➤ [ `.lock` ] **⤳** (Name)
———————————————
بازکردن قفل یک ویژگی
➤ [ `.unlock` ] **⤳** (Name)
———————————————
قفل همه ویژگی ها
➤ [ `.lock all` ]
———————————————
بازکردن قفل همه ویژگی ها
➤ [ `.unlock all` ]
———————————————
"""

fahelp9 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ کرون جاب ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
تنظیم کرون جاب برحسب دقیقه
➤ [ `.cron` ] **⤳** (URL Time)
Time: 1, 2, 5, 10, 15, 30 ...
———————————————
"""

fahelp10 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ آنتی لاگین ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
فعال یا غیرفعال کردن آنتی لاگین اکانت
➤ [ `.antilog` ] **⤳** (on OR off)
———————————————
"""

fahelp11 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ تبچی ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
وضعیت تبچی
➤ [ `.tabchi status` ]
———————————————
فعال یا غیرفعال کردن ارسال خودکار به پیوی ها
➤ [ `.tabchipv` ] **⤳** (on OR off)
———————————————
فعال یا غیرفعال کردن ارسال خودکار به گروه ها
➤ [ `.tabchigp` ] **⤳** (on OR off)
———————————————
تنظیم بنر ارسال خودکار به پیوی ها
➤ [ `.setbannerpv` ] **⤳** (TEXT) (Reply)
———————————————
تنظیم بنر ارسال خودکار به گروه ها
➤ [ `.setbannergp` ] **⤳** (TEXT) (Reply)
———————————————
تنظیم زمان ارسال خودکار به پیوی ها برحسب ثانیه
➤ [ `.settimerpv` ] **⤳** (NUM)
———————————————
تنظیم زمان ارسال خودکار به گروه ها برحسب ثانیه
➤ [ `.settimergp` ] **⤳** (NUM)
———————————————
ارسال همگانی به پیوی ها
➤ [ `.sendpv` ] **⤳** (TEXT) (Reply)
———————————————
ارسال همگانی به گروه ها
➤ [ `.sendgp` ] **⤳** (TEXT) (Reply)
———————————————
تنظیم بنر ارسال به پیوی اعضای گروه
➤ [ `.setbannersender` ] **⤳** (TEXT) (Reply)
———————————————
ارسال به پیوی اعضای گروه مورد نظر
➤ [ `.sendall` ] **⤳** (Username)
———————————————
دریافت لینک گروه
➤ [ `.invitelink` ]
———————————————
پیوستن به گروه
➤ [ `.join` ] **⤳** (Link)
———————————————
خروج از گروه
➤ [ `.leave` ] **⤳** (Link)
———————————————
خروج از تمام گروه ها
➤ [ `.leaveallgc` ]
———————————————
خروج از تمام کانال ها
➤ [ `.leaveallch` ]
———————————————
"""

fahelp12 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ ویرایشگر عکس ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
**با دستورات زیر می‌توانید متن مورد نظر خود را روی عکس طرح کنید**

➤ [ `.kanna` ] **⤳** (TEXT)
———————————————
➤ [ `.clyde` ] **⤳** (TEXT)
———————————————
➤ [ `.write` ] **⤳** (TEXT)
———————————————
➤ [ `.mind` ] **⤳** (TEXT)
———————————————
➤ [ `.trump` ] **⤳** (TEXT)
———————————————
➤ [ `.o` ] **⤳** (TEXT)
———————————————
➤ [ `.o2` ] **⤳** (TEXT)
———————————————
➤ [ `.bish` ] **⤳** (TEXT)
———————————————
➤ [ `.latex` ] **⤳** (TEXT)
———————————————
**با دستورات زیر می‌توانید روی عکس مورد نظر خود فیلتر های مختلف ست کنید**

➤ [ `.blue` ] **⤳** (Reply)
———————————————
➤ [ `.green` ] **⤳** (Reply)
———————————————
➤ [ `.red` ] **⤳** (Reply)
———————————————
➤ [ `.grey` ] **⤳** (Reply)
———————————————
➤ [ `.grey2` ] **⤳** (Reply)
———————————————
➤ [ `.sepia` ] **⤳** (Reply)
———————————————
➤ [ `.threshold` ] **⤳** (Reply)
———————————————
➤ [ `.blurple` ] **⤳** (Reply)
———————————————
➤ [ `.filter` ] **⤳** (Reply)
———————————————
**با دستورات زیر می‌توانید استایل و ابعاد عکس مورد نظر خود را تغییر دهید**

➤ [ `.bisexual` ] **⤳** (Reply)
———————————————
➤ [ `.blur` ] **⤳** (Reply)
———————————————
➤ [ `.horny` ] **⤳** (Reply)
———————————————
➤ [ `.stupid` ] **⤳** (Reply)
———————————————
➤ [ `.lesbian` ] **⤳** (Reply)
———————————————
➤ [ `.lgbt` ] **⤳** (Reply)
———————————————
➤ [ `.lolice` ] **⤳** (Reply)
———————————————
➤ [ `.non` ] **⤳** (Reply)
———————————————
➤ [ `.psexual` ] **⤳** (Reply)
———————————————
➤ [ `.pixel` ] **⤳** (Reply)
———————————————
➤ [ `.simp` ] **⤳** (Reply)
———————————————
➤ [ `.spin` ] **⤳** (Reply)
———————————————
➤ [ `.toni` ] **⤳** (Reply)
———————————————
**با دستورات زیر می‌توانید روی عکس مورد نظر خود فیلتر ها و تغییرات فان ست کنید**

➤ [ `.comrade` ] **⤳** (Reply)
———————————————
➤ [ `.gay` ] **⤳** (Reply)
———————————————
➤ [ `.glass` ] **⤳** (Reply)
———————————————
➤ [ `.jail` ] **⤳** (Reply)
———————————————
➤ [ `.wasted` ] **⤳** (Reply)
———————————————
➤ [ `.pass` ] **⤳** (Reply)
———————————————
"""

fahelp13 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ گیف و لوگو ساز ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
ساخت لوگو با متن
➤ [ `.logo` ] **⤳** (TEXT)
———————————————
ساخت لوگو با متن 2
➤ [ `.logo2` ] **⤳** (TEXT)
———————————————
ساخت لوگو با متن و طرح دلخواه
➤ [ `.lg` ] **⤳** (TEXT Mode)
Mode: 1-138
———————————————
ساخت گیف با متن
➤ [ `.gif` ] **⤳** (TEXT)
———————————————
ساخت گیف با متن 2
➤ [ `.giff` ] **⤳** (TEXT)
———————————————
"""

fahelp14 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ کامپایلر ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
➤ [ `.py` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.js` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.php` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.kotlin` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.go` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.java` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.lua` ] **⤳** (Code) (Reply)
———————————————
➤ [ `.exec` ] **⤳** (Code)
———————————————
"""

fahelp15 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ ابزار ها ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
استخراج فایل از حالت فشرده
➤ [ `.unzip` ] **⤳** (Reply)
———————————————
تغییر نام فایل
➤ [ `.rname` ] **⤳** (TEXT) (Reply)
———————————————
چکر شماره مجازی
➤ [ `.check` ] **⤳** (Number)
———————————————
اسکرین شات از متن
➤ [ `.q` ] **⤳** (Reply)
———————————————
اسکرین شات از متن دلخواه
➤ [ `.qq` ] **⤳** (TEXT)
———————————————
دریافت نتایج بازی های Cricket
➤ [ `.cricket` ] **⤳**
———————————————
وضعیت آب و هوا
➤ [ `.weather` ] **⤳** (City Name)
———————————————
زمان اذان
➤ [ `.azan` ] **⤳** (City Name)
———————————————
تبدیل کننده دما
➤ [ `.t` ] **⤳** (NUM c OR f)
eg: .t 25 c
———————————————
تبدیل کننده ارز دیجیتال
➤ [ `.c` ] **⤳** (NUM Currency1 Currency2)
eg: .c 100 usdt eur
———————————————
ماشین حساب ریاضی
➤ [ `.e` ] **⤳** (Match)
eg: .e 2+2
———————————————
دریافت آیپی سایت
➤ [ `.ip` ] **⤳** (Domain)
———————————————
دریافت اطلاعات آیپی
➤ [ `.whoisip` ] **⤳** (IP)
———————————————
کوتاه کننده لینک
➤ [ `.link` ] **⤳** (URL)
———————————————
کوتاه کننده لینک 2
➤ [ `.link2` ] **⤳** (URL)
———————————————
دریافت پینگ سایت
➤ [ `.p` ] **⤳** (Domain)
———————————————
اسکرین شات از سایت
➤ [ `.screenshot` ] **⤳** (Domain)
———————————————
اسکرین شات از سایت 2
➤ [ `.screenshot2` ] **⤳** (Domain)
———————————————
اسکرین شات از سایت 3
➤ [ `.screenshot3` ] **⤳** (Domain)
———————————————
اسکرین شات از سایت 4
➤ [ `.screenshot4` ] **⤳** (Domain)
———————————————
اسکرین شات از سایت 5
➤ [ `.shot` ] **⤳** (Domain)
———————————————
دریافت اطلاعات اکانت گیت هاب
➤ [ `.github` ] **⤳** (Username)
———————————————
دریافت اطلاعات پروژه
➤ [ `.git` ] **⤳** (TEXT)
———————————————
جستجو در دیکشنری
➤ [ `.dict` ] **⤳** (Word)
———————————————
کپی کردن پروفایل یک اکانت
➤ [ `.clone` ] **⤳** (ID) (Reply)
———————————————
دریافت تاریخ ساخت اکانت
➤ [ `.i` ] **⤳** (ID) (Reply)
———————————————
دریافت تاریخ ساخت اکانت سلف
➤ [ `.creation` ]
———————————————
وضعیت محدودیت اکانت سلف
➤ [ `.limit` ]
———————————————
دریافت اطلاعات کشور
➤ [ `.country` ] **⤳** (Name)
———————————————
تبدیل استیکر به عکس
➤ [ `.tp` ] **⤳** (Reply)
———————————————
تبدیل عکس به استیکر
➤ [ `.ts` ] **⤳** (Reply)
———————————————
ساخت گیف
➤ [ `.tg` ] **⤳** (Reply)
———————————————
ترجمه به فارسی
➤ [ `.fa` ] **⤳** (TEXT)
———————————————
ترجمه به انگلیسی
➤ [ `.en` ] **⤳** (TEXT)
———————————————
دریافت فیلم
➤ [ `.movie` ] **⤳** (TEXT)
———————————————
دریافت انیمه
➤ [ `.anim` ] **⤳** (TEXT)
———————————————
ساخت پسورد با تعداد کاراکتر دلخواه
➤ [ `.pass` ] **⤳** (NUM)
———————————————
تبدیل متن به کد مورس
➤ [ `.morset` ] **⤳** (TEXT)
———————————————
تبدیل کد مورس به متن
➤ [ `.unmorset` ] **⤳** (Code)
———————————————
دریافت تاریخ
➤ [ `.date` ]
———————————————
دریافت اطلاعات یک اکانت
➤ [ `.id` ] **⤳** (ID) (Reply)
———————————————
دریافت اطلاعات یک پیام
➤ [ `.get_message` ] **⤳** (Reply)
———————————————
منشن کردن یک کاربر
➤ [ `.mention` ] **⤳** (ID) (Reply)
———————————————
بررسی صحت کد ملی
➤ [ `.meli` ] **⤳** (Number)
———————————————
استعلام کارت بانکی
➤ [ `.estelam` ] **⤳** (Number)
———————————————
دریافت اخبار روز
➤ [ `.news` ] **⤳** (Category)
Category: business, entertainment, general, health, science, sports, technology
———————————————
دریافت کارت بین
➤ [ `.ccgen` ]
———————————————
دریافت اخبار روز
➤ [ `.yjc` ]
———————————————
استخراج متن از عکس
➤ [ `.ocr` ] **⤳** (Reply)
———————————————
دانلود عکس زمان دار
➤ [ `.dl` ] **⤳** (Reply)
———————————————
ذخیره محتوا در پیام های ذخیره شده
➤ [ `.waitt` ] **⤳** (Reply)
———————————————
دریافت ساعت
➤ [ `.time` ]
———————————————
"""

fahelp16 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ اکانت ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
افزودن ادمین به سلف
➤ [ `.addadmin` ] **⤳** (ID) (Reply)
———————————————
حذف ادمین سلف
➤ [ `.deladmin` ] **⤳** (ID) (Reply)
———————————————
لیست ادمین های سلف
➤ [ `.adminlist` ]
———————————————
پاکسازی لیست ادمین های سلف
➤ [ `.clearadminlist` ]
———————————————
دریافت آیدی عددی اکانت سلف
➤ [ `id` ]
———————————————
وضعیت محدودیت اکانت سلف
➤ [ `.limit` ]
———————————————
دریافت تاریخ ساخت اکانت سلف
➤ [ `.creation` ]
———————————————
دریافت اطلاعات سشن اکانت سلف
➤ [ `.session` ]
———————————————
"""

fahelp17 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ کتاب ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
دریافت جوک
➤ [ `.joke` ]
———————————————
دریافت شعر
➤ [ `.poem` ]
———————————————
دریافت دانستنی
➤ [ `.know` ]
———————————————
دریافت نقل قول
➤ [ `.quote` ]
———————————————
جستجو در ویکی پدیا
➤ [ `.wiki` ] **⤳** (TEXT)
———————————————
جستجو در گوگل
➤ [ `.google` ] **⤳** (TEXT)
———————————————
تبدیل عدد به حروف
➤ [ `.num` ] **⤳** (NUM)
———————————————
دریافت اطلاعات نام
➤ [ `.name` ] **⤳** (Name)
———————————————
دریافت بیوگرافی
➤ [ `.bio` ]
———————————————
دریافت خاطره
➤ [ `.memo` ]
———————————————
دریافت پ ن پ
➤ [ `.pnp` ]
———————————————
دریافت الکی
➤ [ `.alaki` ]
———————————————
دریافت حدیث
➤ [ `.hadis` ]
———————————————
دریافت داستان
➤ [ `.dastan` ]
———————————————
دریافت نام رندوم
➤ [ `.rname` ]
———————————————
دریافت فال
➤ [ `.fal` ]
———————————————
دریافت استخاره
➤ [ `.estekhare` ]
———————————————
دریافت ذکر
➤ [ `.zekr` ]
———————————————
"""

fahelp18 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ سرگرمی ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
تقلب در تاس
➤ [ `.tas` ] **⤳** (1-6)
———————————————
تقلب در دارت
➤ [ `.dart` ]
———————————————
تقلب در بولینگ
➤ [ `.bowling` ]
———————————————
تقلب در بسکتبال
➤ [ `.basketball` ]
———————————————
تCancel در فوتبال
➤ [ `.football` ] **⤳** (1 OR 6)
1: Fail
4: Goal
———————————————
دریافت بازی رندوم 1
➤ [ `.game` ]
———————————————
دریافت بازی رندوم 2
➤ [ `.bazi` ]
———————————————
دریافت بازی رندوم 3
➤ [ `.hehe` ]
———————————————
**سایر سرگرمی ها**

➤ [ `.moon` ]
———————————————
➤ [ `.clock` ]
———————————————
➤ [ `.thunder` ]
———————————————
➤ [ `.earth` ]
———————————————
➤ [ `.heart` ]
———————————————
➤ [ `.love` ]
———————————————
➤ [ `.santet` ]
———————————————
➤ [ `.nah` ]
———————————————
➤ [ `.ajg` ]
———————————————
➤ [ `.babi` ]
———————————————
➤ [ `.tank` ]
———————————————
➤ [ `.y` ]
———————————————
➤ [ `.awk` ]
———————————————
➤ [ `.tembak` ]
———————————————
➤ [ `.heli` ]
———————————————
➤ [ `.gabut` ]
———————————————
➤ [ `.syg` ]
———————————————
➤ [ `.dino` ]
———————————————
➤ [ `.hack` ]
———————————————
➤ [ `.fuck` ]
———————————————
➤ [ `.koc` ]
———————————————
➤ [ `.charging` ]
———————————————
➤ [ `.gang` ]
———————————————
➤ [ `.hypo` ]
———————————————
➤ [ `.ding` ]
———————————————
➤ [ `.wtf` ]
———————————————
➤ [ `.call` ]
———————————————
➤ [ `.bomb` ]
———————————————
➤ [ `.brain` ]
———————————————
➤ [ `.ahh` ]
———————————————
➤ [ `.hmm` ]
———————————————
"""

fahelp19 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ بازار ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
قیمت کالا در بازار ایران (باسلام)
➤ [ `.price` ] **⤳** (TEXT)
———————————————
قیمت کالا در بازار ایران (ترب)
➤ [ `.qeymat` ] **⤳** (TEXT)
———————————————
لیست نماد ارز های دیجیتال
➤ [ `.cryptolist` ]
———————————————
قیمت ارز دیجیتال
➤ [ `.crypto` ] **⤳** (Name)
———————————————
تبدیل کننده ارز دیجیتال
➤ [ `.c` ] **⤳** (NUM Currency1 Currency2)
eg: .c 100 usdt eur
———————————————
قیمت ترون
➤ [ `.trx` ]
———————————————
لیست قیمت ارز ها
➤ [ `.arz` ]
———————————————
استعلام کارت بانکی
➤ [ `.estelam` ] **⤳** (Number)
———————————————
دریافت اطلاعات تراکنش ارز دیجیتال
➤ [ `.tara` ] **⤳** (TransLink)
———————————————
"""

fahelp20 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ استیکر - گیف ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
ساخت استیکر با متن
➤ [ `.sticker` ] **⤳** (TEXT)
———————————————
دریافت اطلاعات استیکر
➤ [ `.stickerinfo` ] **⤳** (Reply)
———————————————
ساخت استیکر با کد ارور
➤ [ `.error` ] **⤳** (Code)
eg: .error 404
———————————————
کوچک کردن استیکر و عکس
➤ [ `.tiny` ] **⤳** (Reply)
———————————————
تبدیل عکس به استیکر
➤ [ `.ts` ] **⤳** (Reply)
———————————————
ساخت گیف
➤ [ `.tg` ] **⤳** (Reply)
———————————————
**دریافت گیف رندوم**

➤ [ `.palm` ]
———————————————
➤ [ `.wink` ]
———————————————
➤ [ `.hug` ]
———————————————
➤ [ `.pat` ]
———————————————
"""

fahelp21 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ هوش مصنوعی ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
**هوش مصنوعی متنی**

➤ [ `.gpt3` ] **⤳** (TEXT)
———————————————
➤ [ `.gpt4` ] **⤳** (TEXT)
———————————————
➤ [ `.bard` ] **⤳** (TEXT)
———————————————
➤ [ `.asq` ] **⤳** (TEXT)
———————————————
➤ [ `.messi` ] **⤳** (TEXT)
———————————————
➤ [ `.ronaldo` ] **⤳** (TEXT)
———————————————
➤ [ `.ilon` ] **⤳** (TEXT)
———————————————
**هوش مصنوعی صوتی**

➤ [ `.` ] **⤳** (TEXT) زن
———————————————
➤ [ `/` ] **⤳** (TEXT) مرد
———————————————
➤ [ `.voice` ] **⤳** (TEXT)
———————————————
➤ [ `.crush` ] **⤳** (TEXT)
———————————————
➤ [ `.wo` ] **⤳** (TEXT) زن
———————————————
➤ [ `.ma` ] **⤳** (TEXT) مرد
———————————————
➤ [ `.v` ] **⤳** (TEXT)
———————————————
دریافت لیست آیدی ها
➤ [ `.vl` ]
———————————————
تنظیم لهجه مورد نظر با آیدی
➤ [ `.sv` ] **⤳** (Mode)
———————————————
**هوش مصنوعی تصویری**

➤ [ `.pgpt` ] **⤳** (TEXT)
———————————————
"""

fahelp22 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ عکس ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
ساخت رنگ
➤ [ `.color` ] **⤳** (Color)
———————————————
**دریافت عکس رندوم حیوانات**

➤ [ `.pikachu` ]
———————————————
➤ [ `.whale` ]
———————————————
➤ [ `.foxx` ]
———————————————
➤ [ `.doggg` ]
———————————————
➤ [ `.rpanda` ]
———————————————
➤ [ `.raccoon` ]
———————————————
➤ [ `.panda` ]
———————————————
➤ [ `.koala` ]
———————————————
➤ [ `.kangroo` ]
———————————————
➤ [ `.fox` ]
———————————————
➤ [ `.dogg` ]
———————————————
➤ [ `.birdd` ]
———————————————
➤ [ `.catt` ]
———————————————
➤ [ `.bird` ]
———————————————
➤ [ `.dog` ]
———————————————
➤ [ `.cat` ]
———————————————
➤ [ `.robo` ] **⤳** (1-999999)
———————————————
**دریافت عکس رندوم +18**

➤ [ `.couple` ]
———————————————
➤ [ `.ayang` ]
———————————————
➤ [ `.boob` ]
———————————————
➤ [ `.nude` ]
———————————————
➤ [ `.nude2` ]
———————————————
**جستجوی عکس**

➤ [ `.pic` ]
———————————————
➤ [ `.bing` ]
———————————————
➤ [ `.uns` ]
———————————————
➤ [ `.photo` ]
———————————————
➤ [ `.photos` ]
———————————————
"""

fahelp23 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ موزیک ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
**جستجو و دریافت موزیک با دستورات زیر**

➤ [ `.music` ] **⤳** (TEXT)
———————————————
➤ [ `.youtube` ] **⤳** (TEXT)
———————————————
➤ [ `.musicc` ] **⤳** (TEXT)
———————————————
➤ [ `.remix` ] **⤳** (TEXT)
———————————————
➤ [ `.demo` ] **⤳** (TEXT)
———————————————
➤ [ `.classic` ] **⤳** (TEXT)
———————————————
➤ [ `.ahang` ] **⤳** (TEXT)
———————————————
➤ [ `.melo` ] **⤳** (TEXT)
———————————————
➤ [ `.global` ] **⤳** (TEXT)
———————————————
"""

fahelp24 = """
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
                                                   **[ تنظیمات سیستم ]**
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
روشن کردن سلف
[ ➤ `.on` ]
———————————————
خاموش کردن سلف
[ ➤ `.off` ]
———————————————
راه اندازی مجدد سلف
➤ [ `.restart` ]
———————————————
غیرفعال کردن اضطراری سلف
➤ [ `.shutdown` ]
———————————————
دریافت پینگ سلف
➤ [ `.ping` ]
———————————————
وضعیت سلف
➤ [ `self` ]
———————————————
دریافت آمار سلف
➤ [ `.on_off_status` ]
———————————————
اطلاعات پردازشگر
➤ [ `.cpu` ]
———————————————
اطلاعات مموری
➤ [ `.memory` ]
———————————————
اطلاعات سیستم
➤ [ `.system-inf` ]
———————————————
"""

# English help texts (brief versions)
enhelp1 = fahelp1.replace("**[ سراسری - شخصی ]**", "**[ Global - Personal ]**")
enhelp2 = fahelp2.replace("**[ پروفایل ]**", "**[ Profile ]**")
enhelp3 = fahelp3.replace("**[ دانلودر ]**", "**[ Downloader ]**")
enhelp4 = fahelp4.replace("**[ آپلودر ]**", "**[ Uploader ]**")
enhelp5 = fahelp5.replace("**[ حالت متن ]**", "**[ Text Mode ]**")
enhelp6 = fahelp6.replace("**[ حالت اکشن ]**", "**[ Action Mode ]**")
enhelp7 = fahelp7.replace("**[ وبهوک ]**", "**[ Webhook ]**")
enhelp8 = fahelp8.replace("**[ قفل ها ]**", "**[ Locks ]**")
enhelp9 = fahelp9.replace("**[ کرون جاب ]**", "**[ Cron Job ]**")
enhelp10 = fahelp10.replace("**[ آنتی لاگین ]**", "**[ Anti Login ]**")
enhelp11 = fahelp11.replace("**[ تبچی ]**", "**[ Tabchi ]**")
enhelp12 = fahelp12.replace("**[ ویرایشگر عکس ]**", "**[ Photo Editor ]**")
enhelp13 = fahelp13.replace("**[ گیف و لوگو ساز ]**", "**[ GIF & Logo Maker ]**")
enhelp14 = fahelp14.replace("**[ کامپایلر ]**", "**[ Compiler ]**")
enhelp15 = fahelp15.replace("**[ ابزار ها ]**", "**[ Tools ]**")
enhelp16 = fahelp16.replace("**[ اکانت ]**", "**[ Account ]**")
enhelp17 = fahelp17.replace("**[ کتاب ]**", "**[ Book ]**")
enhelp18 = fahelp18.replace("**[ سرگرمی ]**", "**[ Fun ]**")
enhelp19 = fahelp19.replace("**[ بازار ]**", "**[ Market ]**")
enhelp20 = fahelp20.replace("**[ استیکر - گیف ]**", "**[ Sticker - GIF ]**")
enhelp21 = fahelp21.replace("**[ هوش مصنوعی ]**", "**[ AI ]**")
enhelp22 = fahelp22.replace("**[ عکس ]**", "**[ Photo ]**")
enhelp23 = fahelp23.replace("**[ موزیک ]**", "**[ Music ]**")
enhelp24 = fahelp24.replace("**[ تنظیمات سیستم ]**", "**[ System ]**")

#================= Dark Pulse Keyboards =================#

openpanelbot = InlineKeyboardMarkup(
     [
         [
             InlineKeyboardButton("Panel", switch_inline_query_current_chat='panel')
         ]
     ]
)

keyboard_idk = ReplyKeyboardMarkup(
     [
         [
             ("Add Admin"),
             ("Delete Admin"),
             ("Admin List")
         ],
         [
             ("Add Owner"),
             ("Delete Owner"),
             ("Owner List")
         ]
     ],
one_time_keyboard=True,resize_keyboard=True)

mark1 = InlineKeyboardMarkup(
     [
          [
               InlineKeyboardButton('سراسری - شخصی',callback_data=f'global_person1-{owner}')
          ],
                              [
               InlineKeyboardButton('سرگرمشو',callback_data=f'global_person3-{owner}'),
               InlineKeyboardButton('راهنما وپنل',callback_data=f'global_person4-{owner}')
          ],
               [
               InlineKeyboardButton('بخش کامنتر',callback_data=f'profile16-{owner}'),
               InlineKeyboardButton('بخش مدیریت',callback_data=f'profile17-{owner}')
          ],
          [
               InlineKeyboardButton('پروفایل',callback_data=f'profile1-{owner}'),
               InlineKeyboardButton('بخش پین و سکوت',callback_data=f'downloader2-{owner}')
          ],
          [
               InlineKeyboardButton('دانلودر',callback_data=f'downloader1-{owner}'),
               InlineKeyboardButton('آپلودر',callback_data=f'uploader1-{owner}')
          ],
          [
               InlineKeyboardButton('حالت متن',callback_data=f'text_mode1-{owner}'),
               InlineKeyboardButton('حالت اکشن',callback_data=f'action_mode1-{owner}')
          ],
          [
               InlineKeyboardButton('وبهوک',callback_data=f'webhook1-{owner}'),
               InlineKeyboardButton('قفل ها',callback_data=f'locks1-{owner}'),
               InlineKeyboardButton('کرون جاب',callback_data=f'cronjob1-{owner}')
          ],
          [
               InlineKeyboardButton('آنتی لاگین',callback_data=f'antilogin1-{owner}'),
               InlineKeyboardButton('تبچی',callback_data=f'tabchi1-{owner}')
          ],
          [
               InlineKeyboardButton('ویرایشگر عکس',callback_data=f'photo_editor1-{owner}'),
               InlineKeyboardButton('گیف و لوگو ساز',callback_data=f'marker1-{owner}')
          ],
          [
               InlineKeyboardButton('کامپایلر',callback_data=f'compiler1-{owner}'),
               InlineKeyboardButton('ابزار ها',callback_data=f'tools1-{owner}'),
               InlineKeyboardButton('اکانت',callback_data=f'account1-{owner}')
          ],
          [
               InlineKeyboardButton('کتاب',callback_data=f'book1-{owner}'),
               InlineKeyboardButton('سرگرمی',callback_data=f'fun1-{owner}'),
               InlineKeyboardButton('بازار',callback_data=f'market1-{owner}')
          ],
          [
               InlineKeyboardButton('استیکر - گیف',callback_data=f'photo_gif1-{owner}'),
               InlineKeyboardButton('هوش مصنوعی',callback_data=f'ai1-{owner}')
          ],
          [
               InlineKeyboardButton('عکس',callback_data=f'photo1-{owner}'),
               InlineKeyboardButton('موزیک',callback_data=f'music1-{owner}')
          ],
          [
               InlineKeyboardButton('تنظیمات سیستم',callback_data=f'system1-{owner}')
          ],
          [
               InlineKeyboardButton('● بستن پنل ●',callback_data=f'close1-{owner}')
          ]
     ]
)

mark2 = InlineKeyboardMarkup(
     [
          [
               InlineKeyboardButton('𝗚𝗹𝗼𝗯𝗮𝗹 - 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹',callback_data=f'global_person2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗣𝗿𝗼𝗳𝗶𝗹𝗲',callback_data=f'profile2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗿',callback_data=f'downloader2-{owner}'),
               InlineKeyboardButton('𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗿',callback_data=f'uploader2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗧𝗲𝘅𝘁 𝗠𝗼𝗱𝗲',callback_data=f'text_mode2-{owner}'),
               InlineKeyboardButton('𝗔𝗰𝘁𝗶𝗼𝗻 𝗠𝗼𝗱𝗲',callback_data=f'action_mode2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗪𝗲𝗯𝗵𝗼𝗼𝗸',callback_data=f'webhook2-{owner}'),
               InlineKeyboardButton('𝗟𝗼𝗰𝗸𝘀',callback_data=f'locks2-{owner}'),
               InlineKeyboardButton('𝗖𝗿𝗼𝗻 𝗝𝗼𝗯',callback_data=f'cronjob2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗔𝗻𝘁𝗶 𝗟𝗼𝗴𝗶𝗻',callback_data=f'antilogin2-{owner}'),
               InlineKeyboardButton('𝗧𝗮𝗯𝗰𝗵𝗶',callback_data=f'tabchi2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗣𝗵𝗼𝘁𝗼 𝗘𝗱𝗶𝘁𝗼𝗿',callback_data=f'photo_editor2-{owner}'),
               InlineKeyboardButton('𝗟 - 𝗚 𝗠𝗮𝗿𝗸𝗲𝗿',callback_data=f'marker2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗖𝗼𝗺𝗽𝗶𝗹𝗲𝗿',callback_data=f'compiler2-{owner}'),
               InlineKeyboardButton('𝗧𝗼𝗼𝗹𝘀',callback_data=f'tools2-{owner}'),
               InlineKeyboardButton('𝗔𝗰𝗰𝗼𝘂𝗻𝘁',callback_data=f'account2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗕𝗼𝗼𝗸',callback_data=f'book2-{owner}'),
               InlineKeyboardButton('𝗙𝘂𝗻',callback_data=f'fun2-{owner}'),
               InlineKeyboardButton('𝗠𝗮𝗿𝗸𝗲𝘁',callback_data=f'market2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗦𝘁𝗶𝗰𝗸𝗲𝗿 - 𝗚𝗶𝗳',callback_data=f'photo_gif2-{owner}'),
               InlineKeyboardButton('𝗔𝗜',callback_data=f'ai2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗣𝗵𝗼𝘁𝗼',callback_data=f'photo2-{owner}'),
               InlineKeyboardButton('𝗠𝘂𝘀𝗶𝗰',callback_data=f'music2-{owner}')
          ],
          [
               InlineKeyboardButton('𝗦𝘆𝘀𝘁𝗲𝗺',callback_data=f'system2-{owner}')
          ],
          [
               InlineKeyboardButton('● 𝗖𝗹𝗼𝘀𝗲 𝗣𝗮𝗻𝗲𝗹 ●',callback_data=f'close2-{owner}')
          ]
     ]
)

dast1 = InlineKeyboardMarkup(
     [
          [
               InlineKeyboardButton("● بازگشت ●", callback_data=f'back1-{owner}')
          ]
     ]
)

dast2 = InlineKeyboardMarkup(
     [
          [
               InlineKeyboardButton("● 𝗕𝗮𝗰𝗸 ●", callback_data=f'back2-{owner}')
          ]
     ]
)

#================= Handlers =================#

@app.on_inline_query()
async def answer(client, inline_query):
     chat_id = inline_query.from_user.id
     AdminUser = get_data(f"SELECT * FROM adminlist WHERE id = {chat_id} LIMIT 1")
     if AdminUser is not None:
          if inline_query.query == "panel":
               try:
                    user = await client.get_users(chat_id)
                    card_path = await render_titan_user_card_cached(client, user)
                    languages = InlineKeyboardMarkup(
                         [
                              [
                                   InlineKeyboardButton('فارسی 🇮🇷',callback_data=f'persian-{inline_query.from_user.id}')
                              ],
                              [
                                   InlineKeyboardButton('🇬🇧 English',callback_data=f'english-{inline_query.from_user.id}')
                              ]
                         ]
                    )
                    await inline_query.answer(
                         results=[
                              InlineQueryResultPhoto(
                                   title="TiTaN Panel",
                                   photo_file_id=card_path,
                                   caption="**زبان پنل را انتخاب کنید / Choose panel language:**",
                                   description="Helper Panel",
                                   reply_markup=languages,
                                   thumb_url="https://via.placeholder.com/1280x853"
                              ),
                         ],
                         cache_time=1
                    )
               except Exception:
                    languages = InlineKeyboardMarkup(
                         [
                              [
                                   InlineKeyboardButton('فارسی 🇮🇷',callback_data=f'persian-{inline_query.from_user.id}')
                              ],
                              [
                                   InlineKeyboardButton('🇬🇧 English',callback_data=f'english-{inline_query.from_user.id}')
                              ]
                         ]
                    )
                    await inline_query.answer(
                         results=[
                              InlineQueryResultArticle(
                                   title="Helper",
                                   input_message_content=InputTextMessageContent(f"**سلام {inline_query.from_user.first_name} خوش آمدید. لطفا یک زبان انتخاب کنید:\\n\\nHi {inline_query.from_user.first_name} Welcome. Please select a language:**"),
                                   description="Helper Panel",
                                   reply_markup=languages
                              ),
                         ],
                         cache_time=1
                    )

          if inline_query.query == "coinprice":
               s = requests.get('https://api.nobitex.ir/market/stats?srcCurrency=usdt,trx,ton,btc,shib,eth,etc,usdt,ada,bch,ltc,bnb&dstCurrency=irt,rls,usdt')
               s = s.text
               js = json.loads(s)
               byusdt = js['stats']['usdt-irt']['bestBuy']
               sellusdt = js['stats']['usdt-irt']['bestSell']
               bytrx = js['stats']['trx-irt']['bestBuy']
               selltrx = js['stats']['trx-irt']['bestSell']
               byton = js['stats']['ton-irt']['bestBuy']
               sellton = js['stats']['ton-irt']['bestSell']
               byshib = js['stats']['shib-usdt']['bestBuy']
               sellshib = js['stats']['shib-usdt']['bestSell']
               bybit = js['stats']['btc-usdt']['bestBuy']
               sellbit = js['stats']['btc-usdt']['bestSell']
               byet = js['stats']['eth-usdt']['bestBuy']
               sellet = js['stats']['eth-usdt']['bestSell']
               byetc = js['stats']['etc-usdt']['bestBuy']
               selletc = js['stats']['etc-usdt']['bestSell']
               byada = js['stats']['ada-usdt']['bestBuy']
               sellada = js['stats']['ada-usdt']['bestSell']
               bybch = js['stats']['bch-usdt']['bestBuy']
               sellbch = js['stats']['bch-usdt']['bestSell']
               byltc = js['stats']['ltc-usdt']['bestBuy']
               sellltc = js['stats']['ltc-usdt']['bestSell']
               bybnb = js['stats']['bnb-usdt']['bestBuy']
               sellbnb = js['stats']['bnb-usdt']['bestSell']

               coind = InlineKeyboardMarkup(
                    [
                         [
                              InlineKeyboardButton("Currency", callback_data="outside"),
                              InlineKeyboardButton("Best Buy", callback_data="outside"),
                              InlineKeyboardButton("Best Sell", callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("USDT", callback_data="outside"),
                              InlineKeyboardButton("☫%s" % byusdt, callback_data="outside"),
                              InlineKeyboardButton("☫%s" % sellusdt, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("TRX", callback_data="outside"),
                              InlineKeyboardButton("☫%s" % bytrx, callback_data="outside"),
                              InlineKeyboardButton("☫%s" % selltrx, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("TON", callback_data="outside"),
                              InlineKeyboardButton("☫%s" % byton, callback_data="outside"),
                              InlineKeyboardButton("☫%s" % sellton, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("SHIB", callback_data="outside"),
                              InlineKeyboardButton("$%s" % byshib, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellshib, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("BTC", callback_data="outside"),
                              InlineKeyboardButton("$%s" % bybit, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellbit, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("ETH", callback_data="outside"),
                              InlineKeyboardButton("$%s" % byet, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellet, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("ETC", callback_data="outside"),
                              InlineKeyboardButton("$%s" % byetc, callback_data="outside"),
                              InlineKeyboardButton("$%s" % selletc, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("ADA", callback_data="outside"),
                              InlineKeyboardButton("$%s" % byada, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellada, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("BCH", callback_data="outside"),
                              InlineKeyboardButton("$%s" % bybch, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellbch, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("LTC", callback_data="outside"),
                              InlineKeyboardButton("$%s" % byltc, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellltc, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("BNB", callback_data="outside"),
                              InlineKeyboardButton("$%s" % bybnb, callback_data="outside"),
                              InlineKeyboardButton("$%s" % sellbnb, callback_data="outside")
                         ],
                         [
                              InlineKeyboardButton("Close ×", callback_data=f'Close-{inline_query.from_user.id}')
                         ]
                    ]
               )

               await inline_query.answer(
                    results=[
                         InlineQueryResultArticle(
                              title="Coin price",
                              input_message_content=InputTextMessageContent("➣ **Currency price list**"),
                              url="https://t.me/KING_MEMBEER",
                              description="ᴄʀɪᴛᴜs",
                              thumb_url="https://t.me/KING_MEMBEER/33",
                              reply_markup=coind
                         ),
                    ],
                    cache_time=1
               )

@app.on_callback_query()
async def call(app, call):
     AdminUser = get_data(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1")
     if AdminUser is None:
          await call.answer("دسترسی غیر مجاز 🚫", show_alert=False)
          return

     if call.data != "outside":
          if AdminUser is not None and int(call.from_user.id) == int(call.data.split("-")[1]):

              # Language selection
              if call.data.split("-")[0] == "persian":
                   try:
                        user = await app.get_users(call.from_user.id)
                        card_path = await render_titan_user_card_cached(app, user)
                        await app.edit_inline_media(
                             inline_message_id=call.inline_message_id,
                             media=InputMediaPhoto(
                                  media=card_path,
                                  caption=f"**سلام {user.first_name} به راهنمای ونوس سلف خوش آمدید. لطفا بخش مورد نظر خود را انتخاب کنید:**"
                             ),
                             reply_markup=mark1
                        )
                   except Exception:
                        await app.edit_inline_text(
                             inline_message_id=call.inline_message_id,
                             text=f"**سلام {call.from_user.first_name} به راهنمای ونوس سلف خوش آمدید. لطفا بخش مورد نظر خود را انتخاب کنید:**",
                             reply_markup=mark1
                        )
                   await call.answer()
                   return

              if call.data.split("-")[0] == "english":
                   try:
                        user = await app.get_users(call.from_user.id)
                        card_path = await render_titan_user_card_cached(app, user)
                        await app.edit_inline_media(
                             inline_message_id=call.inline_message_id,
                             media=InputMediaPhoto(
                                  media=card_path,
                                  caption=f"**Hello {user.first_name} Welcome to Wenos Self help.\\nPlease select the section you want:**"
                             ),
                             reply_markup=mark2
                        )
                   except Exception:
                        await app.edit_inline_text(
                             inline_message_id=call.inline_message_id,
                             text=f"**Hello {call.from_user.first_name} Welcome to Wenos Self help.\\nPlease select the section you want:**",
                             reply_markup=mark2
                        )
                   await call.answer()
                   return

              # Back handlers
              if call.data.split("-")[0] == "back1":
                   try:
                        user = await app.get_users(call.from_user.id)
                        card_path = await render_titan_user_card_cached(app, user)
                        await app.edit_inline_media(
                             inline_message_id=call.inline_message_id,
                             media=InputMediaPhoto(
                                  media=card_path,
                                  caption=f"**سلام {user.first_name} به راهنمای ونوس سلف خوش آمدید. لطفا بخش مورد نظر خود را انتخاب کنید:**"
                             ),
                             reply_markup=mark1
                        )
                   except Exception:
                        await app.edit_inline_text(
                             inline_message_id=call.inline_message_id,
                             text=f"**سلام {call.from_user.first_name} به راهنمای ونوس سلف خوش آمدید. لطفا بخش مورد نظر خود را انتخاب کنید:**",
                             reply_markup=mark1
                        )
                   await call.answer()
                   return

              if call.data.split("-")[0] == "back2":
                   try:
                        user = await app.get_users(call.from_user.id)
                        card_path = await render_titan_user_card_cached(app, user)
                        await app.edit_inline_media(
                             inline_message_id=call.inline_message_id,
                             media=InputMediaPhoto(
                                  media=card_path,
                                  caption=f"**Hello {user.first_name} Welcome to Wenos Self help.\\nPlease select the section you want:**"
                             ),
                             reply_markup=mark2
                        )
                   except Exception:
                        await app.edit_inline_text(
                             inline_message_id=call.inline_message_id,
                             text=f"**Hello {call.from_user.first_name} Welcome to Wenos Self help.\\nPlease select the section you want:**",
                             reply_markup=mark2
                        )
                   await call.answer()
                   return

              # Category handlers (Persian)
              fa_categories = {
                  "global_person1": fahelp1, "profile1": fahelp2, "downloader1": fahelp3,
                  "uploader1": fahelp4, "text_mode1": fahelp5, "action_mode1": fahelp6,
                  "webhook1": fahelp7, "locks1": fahelp8, "cronjob1": fahelp9,
                  "antilogin1": fahelp10, "tabchi1": fahelp11, "photo_editor1": fahelp12,
                  "marker1": fahelp13, "compiler1": fahelp14, "tools1": fahelp15,
                  "account1": fahelp16, "book1": fahelp17, "fun1": fahelp18,
                  "market1": fahelp19, "photo_gif1": fahelp20, "ai1": fahelp21,
                  "photo1": fahelp22, "music1": fahelp23, "system1": fahelp24,
                  "global_person3": saeed1, "global_person4": saeed2,
                  "profile16": saeed5, "profile17": saeed6, "downloader2": saeed16,
              }
              if call.data.split("-")[0] in fa_categories:
                   await app.edit_inline_text(
                        inline_message_id=call.inline_message_id,
                        text=fa_categories[call.data.split("-")[0]],
                        reply_markup=dast1
                   )
                   await call.answer()
                   return

              # Category handlers (English)
              en_categories = {
                  "global_person2": enhelp1, "profile2": enhelp2, "downloader2": enhelp3,
                  "uploader2": enhelp4, "text_mode2": enhelp5, "action_mode2": enhelp6,
                  "webhook2": enhelp7, "locks2": enhelp8, "cronjob2": enhelp9,
                  "antilogin2": enhelp10, "tabchi2": enhelp11, "photo_editor2": enhelp12,
                  "marker2": enhelp13, "compiler2": enhelp14, "tools2": enhelp15,
                  "account2": enhelp16, "book2": enhelp17, "fun2": enhelp18,
                  "market2": enhelp19, "photo_gif2": enhelp20, "ai2": enhelp21,
                  "photo2": enhelp22, "music2": enhelp23, "system2": enhelp24,
              }
              if call.data.split("-")[0] in en_categories:
                   await app.edit_inline_text(
                        inline_message_id=call.inline_message_id,
                        text=en_categories[call.data.split("-")[0]],
                        reply_markup=dast2
                   )
                   await call.answer()
                   return

              # Close handlers
              if call.data.split("-")[0] == "close1":
                   await app.edit_inline_text(inline_message_id=call.inline_message_id, text="**● پنل راهنما بسته شد ●**")
                   await call.answer()
                   return
              if call.data.split("-")[0] == "close2":
                   await app.edit_inline_text(inline_message_id=call.inline_message_id, text="**● Helper Panel Closed ●**")
                   await call.answer()
                   return
              if call.data.split("-")[0] == "Close":
                   await app.edit_inline_text(inline_message_id=call.inline_message_id, text="**● Closed ●**")
                   await call.answer()
                   return
          else:
               await call.answer("دسترسی غیر مجاز 🚫", show_alert=False)
     else:
          await call.answer("این دکمه نمایشی است", show_alert=True)

#================= Commands =================#

@app.on_message(filters.private & filters.command("restart"), group=1)
async def updates(app, m:Message):
     OwnerUser = get_data(f"SELECT * FROM ownerlist WHERE id = '{m.chat.id}' LIMIT 1")
     if OwnerUser is not None:
          await app.send_message(m.chat.id, "**Helper Restart was successful**")
          python = sys.executable
          os.execl(python, python, *sys.argv)
          update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")

@app.on_message(filters.private & filters.command("panel"))
async def updates(app, m:Message):
     OwnerUser = get_data(f"SELECT * FROM ownerlist WHERE id = '{m.chat.id}' LIMIT 1")
     if OwnerUser is not None:
          try:
               user = await app.get_users(m.from_user.id)
               card_path = await render_titan_user_card_cached(app, user)
               await app.send_photo(
                    m.chat.id,
                    photo=card_path,
                    caption="**زبان پنل را انتخاب کنید / Choose panel language:**",
                    reply_markup=InlineKeyboardMarkup([
                         [InlineKeyboardButton('فارسی 🇮🇷', callback_data=f'persian-{m.from_user.id}')],
                         [InlineKeyboardButton('🇬🇧 English', callback_data=f'english-{m.from_user.id}')],
                    ]))
          except Exception:
               await app.send_message(m.chat.id, "**QuiteCreateCliBot Panel Owner**", reply_markup=keyboard_idk)
          update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")

@app.on_message(filters.private & filters.command("start"))
async def updates(app, m:Message):
     AdminUser = get_data(f"SELECT * FROM adminlist WHERE id = '{m.chat.id}' LIMIT 1")
     if AdminUser is not None:
          await app.send_message(m.chat.id, f"𝑯𝒆𝒍𝒍𝒐 {m.from_user.first_name}\\n𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝑻𝒐 𝑯𝒆𝒍𝒑𝒆𝒓 𝑩𝒐𝒕 💛\\n𝑭𝒐𝒓 𝒈𝒆𝒕 𝑷𝒂𝒏𝒆𝒍 𝒕𝒚𝒑𝒆 ( `help` 𝑶𝒓 `panel` 𝑶𝒓 `پنل` )\\n     ", reply_markup=openpanelbot)
          update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
     else:
          await m.delete()

#================= Owner Panel =================#

Back = ReplyKeyboardMarkup(
     [
          [
               ("Back")
          ]
     ],resize_keyboard=True
)

@app.on_message(filters.private)
async def updates(app, m:Message):
 OwnerUser = get_data(f"SELECT * FROM ownerlist WHERE id = '{m.chat.id}' LIMIT 1")
 if OwnerUser is not None:
     user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
     OwnerList = get_datas("SELECT * FROM ownerlist")
     AdminList = get_datas("SELECT * FROM adminlist")
     text = m.text

     if text == "Back":
          await app.send_message(m.chat.id, "**QuiteCreateCliBot Panel Owner**", reply_markup=keyboard_idk)
          update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")

     elif text == "Add Admin":
          await app.send_message(m.chat.id, "**Send Me User ID**:", reply_markup=Back)
          update_data(f"UPDATE user SET step = 'addadmin' WHERE id = '{m.chat.id}' LIMIT 1")

     elif user["step"] == "addadmin":
          if text.isdigit():
               user_id = int(text.strip())
               if get_data(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is None:
                    await app.send_message(m.chat.id, f"Successfull\\nUser [ `{user_id}` ] Added to Admin List")
                    update_data(f"INSERT INTO adminlist(id) VALUES({user_id})")
               else:
                    await app.send_message(m.chat.id, "This user in the Admin list")
          else:
               await app.send_message(m.chat.id, "Invalid entry! Only sending numbers is allowed")

     elif text == "Delete Admin":
          await app.send_message(m.chat.id, "**Send Me User ID**:", reply_markup=Back)
          update_data(f"UPDATE user SET step = 'deladmin' WHERE id = '{m.chat.id}' LIMIT 1")

     elif user["step"] == "deladmin":
          if text.isdigit():
               user_id = int(text.strip())
               if get_data(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is not None:
                    await app.send_message(m.chat.id, f"Successfull\\nUser [ `{user_id}` ] Deleted From User List")
                    update_data(f"DELETE FROM adminlist WHERE id = '{user_id}' LIMIT 1")
               else:
                    await app.send_message(m.chat.id, f"This user not in Admin list")
          else:
               await app.send_message(m.chat.id, "Invalid entry! Only sending numbers is allowed")

     elif text == "Admin List":
          s = ""
          if AdminList:
               for index, user in enumerate(AdminList, start=1):
                    s += f"֍ {index} -> `{user[0]}`\\n"
               await app.send_message(m.chat.id, f"**Admin List:**\\n{s}")
          else:
               await app.send_message(m.chat.id, f"**Admin List is Empty**")
          update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")

     elif text == "Add Owner":
          await app.send_message(m.chat.id, "**Send Me User ID**:", reply_markup=Back)
          update_data(f"UPDATE user SET step = 'addowner' WHERE id = '{m.chat.id}' LIMIT 1")

     elif user["step"] == "addowner":
          if text.isdigit():
               user_id = int(text.strip())
               if get_data(f"SELECT * FROM ownerlist WHERE id = '{user_id}' LIMIT 1") is None:
                    if get_data(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is not None:
                         await app.send_message(m.chat.id, f"Successfull\\nUser [ `{user_id}` ] Added to Owner List")
                         update_data(f"INSERT INTO ownerlist(id) VALUES({user_id})")
                    else:
                         await app.send_message(m.chat.id, "ابتدا کاربر مورد نظر را به لیست ادمین اضافه کنید!")
               else:
                    await app.send_message(m.chat.id, "This user in the Owner list")
          else:
               await app.send_message(m.chat.id, "Invalid entry! Only sending numbers is allowed")

     elif text == "Delete Owner":
          await app.send_message(m.chat.id, "**Send Me User ID**:", reply_markup=Back)
          update_data(f"UPDATE user SET step = 'delowner' WHERE id = '{m.chat.id}' LIMIT 1")

     elif user["step"] == "delowner":
          if text.isdigit():
               user_id = int(text.strip())
               if get_data(f"SELECT * FROM ownerlist WHERE id = '{user_id}' LIMIT 1") is not None:
                    await app.send_message(m.chat.id, f"Successfull\\nUser [ `{user_id}` ] Deleted From User List")
                    update_data(f"DELETE FROM ownerlist WHERE id = '{user_id}' LIMIT 1")
               else:
                    await app.send_message(m.chat.id, f"This user not in Owner list")
          else:
               await app.send_message(m.chat.id, "Invalid entry! Only sending numbers is allowed")

     elif text == "Owner List":
          s = ""
          if OwnerList:
               for index, user in enumerate(OwnerList, start=1):
                    s += f"֍ {index} -> `{user[0]}`\\n"
               await app.send_message(m.chat.id, f"**Owner List:**\\n{s}")
          else:
               await app.send_message(m.chat.id, f"**Owner List is Empty**")
          update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")

#================= Run =================#

app.start(), print(Fore.YELLOW+"Started..."), idle(), app.stop()