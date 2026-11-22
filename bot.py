#============ In The Name Of God ============#
#                                   𝒹𝒶𝓇𝓀℘𝓊ℓ𝓈

# Source Name: DarkPulse
# @meri_5280
#===========================================#

from colorama import Fore, Style
from pyrogram import Client, filters, idle, errors
from pyrogram.types import *
from functools import wraps
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import subprocess
import html
import zipfile
import pymysql
import shutil
import signal
import re
import os
import jdatetime
import random
import string

# ==================== Config =====================#
Admin = 0 
Token = "0" 
API_ID = 0 
API_HASH = "0" 
Channel_ID = "0" 
Helper_ID = "0" 
DBName = "0" 
DBUser = "0" 
DBPass = "0" 
HelperDBName = "0"
HelperDBUser = "0" 
HelperDBPass = "0" 
CardNumber = "0"
CardName = "0"
# ==================== Create =====================#
if not os.path.isdir("sessions"):
    os.mkdir("sessions")
if not os.path.isdir("selfs"):
    os.mkdir("selfs")
if not os.path.isdir("source"):
    os.mkdir("source")
# ===================== App =======================#
app = Client("Bot", api_id=API_ID, api_hash=API_HASH, bot_token=Token)

scheduler = AsyncIOScheduler()
scheduler.start()

temp_Client = {}
lock = asyncio.Lock()

# ==================== Emojis =====================#
EMOJI_LIST = ["✨", "🌟", "💫", "⭐", "🔥", "💎", "🎯", "🚀", "🛸", "🌈", "🌠", "🎇", "🎆", "💥", "⚡", "💯", "❤️", "💙", "💚", "💛", "💜", "🖤", "🤍", "🤎", "♥️", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝"]

def get_random_emoji():
    return random.choice(EMOJI_LIST)

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

def helper_getdata(query):
    with pymysql.connect(host="localhost", database=HelperDBName, user=HelperDBUser, password=HelperDBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        result = db.fetchone()
        return result

def helper_updata(query):
    with pymysql.connect(host="localhost", database=HelperDBName, user=HelperDBUser, password=HelperDBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        connect.commit()

# ==================== Gift Codes =====================#
update_data("""
CREATE TABLE IF NOT EXISTS gift_codes(
code varchar(20) PRIMARY KEY,
amount bigint DEFAULT '0',
expir_days bigint DEFAULT '0',
max_uses bigint DEFAULT '1',
used_count bigint DEFAULT '0'
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS used_gift_codes(
id bigint,
code varchar(20),
PRIMARY KEY (id, code)
) default charset=utf8mb4;
""")

# ==================== Database Setup =====================#
update_data("""
CREATE TABLE IF NOT EXISTS bot(
status varchar(10) DEFAULT 'ON'
) default charset=utf8mb4;
""")
update_data("""
CREATE TABLE IF NOT EXISTS user(
id bigint PRIMARY KEY,
step varchar(150) DEFAULT 'none',
phone varchar(150) DEFAULT NULL,
amount bigint DEFAULT '0',
expir bigint DEFAULT '0',
account varchar(50) DEFAULT 'unverified',
self varchar(50) DEFAULT 'inactive',
pid bigint DEFAULT NULL
) default charset=utf8mb4;
""")
update_data("""
CREATE TABLE IF NOT EXISTS block(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")
helper_updata("""
CREATE TABLE IF NOT EXISTS ownerlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")
helper_updata("""
CREATE TABLE IF NOT EXISTS adminlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")

bot = get_data("SELECT * FROM bot")
if bot is None:
    update_data("INSERT INTO bot() VALUES()")

OwnerUser = helper_getdata(f"SELECT * FROM ownerlist WHERE id = '{Admin}' LIMIT 1")
if OwnerUser is None:
    helper_updata(f"INSERT INTO ownerlist(id) VALUES({Admin})")

AdminUser = helper_getdata(f"SELECT * FROM adminlist WHERE id = '{Admin}' LIMIT 1")
if AdminUser is None:
    helper_updata(f"INSERT INTO adminlist(id) VALUES({Admin})")

def add_admin(user_id):
    if helper_getdata(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is None:
        helper_updata(f"INSERT INTO adminlist(id) VALUES({user_id})")

def delete_admin(user_id):
    if helper_getdata(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is not None:
        helper_updata(f"DELETE FROM adminlist WHERE id = '{user_id}' LIMIT 1")

def checker(func):
    @wraps(func)
    async def wrapper(c, m, *args, **kwargs):
        chat_id = m.chat.id if hasattr(m, "chat") else m.from_user.id
        bot = get_data("SELECT * FROM bot")
        block = get_data(f"SELECT * FROM block WHERE id = '{chat_id}' LIMIT 1")

        if block is not None and chat_id != Admin:
            return
        
        try:
            await app.get_chat_member(Channel_ID, chat_id)
        except errors.UserNotParticipant:
            await app.send_message(chat_id, f"{get_random_emoji()} لطفا برای استفاده از ربات ابتدا در کانال زیر عضو شوید\nبعد از عضویت روی /start کلیک کنید", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} عضویت در کانال", url=f"https://t.me/{Channel_ID}")
                    ]
                ]
            ))
            return
        except errors.ChatAdminRequired:
            if chat_id == Admin:
                await app.send_message(Admin, f"{get_random_emoji()} ربات برای فعال شدن جوین اجباری در کانال مورد نظر ادمین نمی باشد!\nلطفا ربات را با دسترسی های لازم در کانال مورد نظر ادمین کنید")
            return

        if bot["status"] == "OFF" and chat_id != Admin:
            await app.send_message(chat_id, f"{get_random_emoji()} ربات در حال حاضر خاموش است!")
            return
        
        return await func(c, m, *args, **kwargs)
    return wrapper

async def expirdec(user_id):
    user = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
    user_expir = user["expir"]
    if user_expir > 0:
        user_upexpir = user_expir - 1
        update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
    else:
        job = scheduler.get_job(str(user_id))
        if job:
            scheduler.remove_job(str(user_id))
        if user_id != Admin:
            delete_admin(user_id)
        if os.path.isdir(f"selfs/self-{user_id}"):
            pid = user["pid"]
            try:
                os.kill(pid, signal.SIGKILL)
            except:
                pass
            await asyncio.sleep(1)
            try:
                shutil.rmtree(f"selfs/self-{user_id}")
            except:
                pass
        if os.path.isfile(f"sessions/{user_id}.session"):
            try:
                async with Client(f"sessions/{user_id}") as user_client:
                    await user_client.log_out()
            except:
                pass
            if os.path.isfile(f"sessions/{user_id}.session"):
                os.remove(f"sessions/{user_id}.session")
        if os.path.isfile(f"sessions/{user_id}.session-journal"):
            os.remove(f"sessions/{user_id}.session-journal")
        await app.send_message(user_id, f"{get_random_emoji()} کاربر گرامی اشتراک سلف شما به پایان رسید. برای خرید مجدد اشتراک به قسمت خرید اشتراک مراجعه کنید")
        update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET pid = NULL WHERE id = '{user_id}' LIMIT 1")

async def setscheduler(user_id):
    job = scheduler.get_job(str(user_id))
    if not job:
        scheduler.add_job(expirdec, "interval", hours=24, args=[user_id], id=str(user_id))

def generate_gift_code(length=10):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

Main = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} حساب کاربری", callback_data="MyAccount")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} خرید اشتراک", callback_data="BuySub")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} قیمت پنل ها", callback_data="Price"),
            InlineKeyboardButton(text=f"{get_random_emoji()} کیف پول", callback_data="Wallet")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} احراز هویت", callback_data="AccVerify"),
            InlineKeyboardButton(text=f"{get_random_emoji()} اطلاعات اشتراک", callback_data="Subinfo")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} کد هدیه", callback_data="GiftCode")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} سوالات متداول", url="https://t.me/Group_DarkPulse"),
            InlineKeyboardButton(text=f"{get_random_emoji()} سلف چیست؟", callback_data="WhatSelf")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} پشتیبانی مالی", url="https://t.me/Meti_5280"),
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} پشتیبانی فنی", callback_data="Support")
        ]
    ]
)

AdminPanel = ReplyKeyboardMarkup(
    [
        [
            ("آمار 📊")
        ],
        [
            ("ارسال همگانی ✉️"),
            ("فوروارد همگانی ✉️")
        ],
        [
            ("بلاک کاربر 🚫"),
            ("آنبلاک کاربر ✅️")
        ],
        [
            ("افزودن موجودی ➕"),
            ("کسر موجودی ➖")
        ],
        [
            ("افزودن زمان اشتراک ➕"),
            ("کسر زمان اشتراک ➖")
        ],
        [
            ("فعال کردن سلف 🔵"),
            ("غیرفعال کردن سلف 🔴")
        ],
        [
            ("روشن کردن ربات 🔵"),
            ("خاموش کردن ربات 🔴")
        ],
        [
            ("مدیریت کدهای هدیه 🎁")
        ],
        [
            ("ریست سلف کاربران 🔄")
        ],
        [
            ("حذف کامل سلف کاربر ❌")
        ],
        [
            ("صفحه اصلی 🏠")
        ]
    ],resize_keyboard=True
)

GiftCodePanel = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} ایجاد کد هدیه", callback_data="CreateGiftCode")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} لیست کدهای هدیه", callback_data="ListGiftCodes")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} حذف کد هدیه", callback_data="DeleteGiftCode")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت به پنل", callback_data="BackToPanel")
        ]
    ]
)

ResetConfirm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} بله، ریست کن", callback_data="ConfirmReset")
        ],
        [
            InlineKeyboardButton(text=f"{get_random_emoji()} خیر، برگشت", callback_data="CancelReset")
        ]
    ]
)

AdminBack = ReplyKeyboardMarkup(
    [
        [
            ("برگشت ↪️")
        ]
    ],resize_keyboard=True
)

@app.on_message(filters.private, group=-1)
async def update(c, m):
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    if user is None:
        update_data(f"INSERT INTO user(id) VALUES({m.chat.id})")

@app.on_message(filters.private & filters.command("start"))
@checker
async def start_command(c, m):
    welcome_text = f"""
{get_random_emoji()} سلام کاربر {html.escape(m.chat.first_name)} {get_random_emoji()}
به سلف ساز Dark Pulse خوش آمدید! {get_random_emoji()}

{get_random_emoji()} اینجا میتونی سلف خودت رو بسازی و مدیریت کنی
{get_random_emoji()} از امکانات ویژه ربات استفاده کنی
{get_random_emoji()} و کلی کارهای جالب دیگه انجام بدی!

لطفا از منوی زیر گزینه مورد نظرت رو انتخاب کن:
"""
    await app.send_message(m.chat.id, welcome_text, reply_markup=Main)
    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
    async with lock:
        if m.chat.id in temp_Client:
            del temp_Client[m.chat.id]
    if os.path.isfile(f"sessions/{m.chat.id}.session") and not os.path.isfile(f"sessions/{m.chat.id}.session-journal"):
        os.remove(f"sessions/{m.chat.id}.session")

@app.on_message(filters.private & filters.command("panel"))
@checker
async def panel_command(c, m):
    if m.chat.id == Admin:
        await app.send_message(Admin, f"{get_random_emoji()} مدیر گرامی به پنل مدیریت Dark Pulse خوش آمدید!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]
    else:
        await app.send_message(m.chat.id, f"{get_random_emoji()} شما دسترسی به این بخش را ندارید!")

@app.on_callback_query()
@checker
async def call(c, call):
    global temp_Client
    user = get_data(f"SELECT * FROM user WHERE id = '{call.from_user.id}' LIMIT 1")
    phone_number = user["phone"]
    account_status = "تایید شده" if user["account"] == "verified" else "تایید نشده"
    expir = user["expir"]
    amount = user["amount"]
    chat_id = call.from_user.id
    m_id = call.message.id
    data = call.data
    username = f"@{call.from_user.username}" if call.from_user.username else "وجود ندارد"

    # محاسبه تاریخ انقضا شمسی
    expiration_date = jdatetime.datetime.now() + jdatetime.timedelta(days=expir)
    expiration_date_str = expiration_date.strftime('%Y/%m/%d') # تاریخ به فرمت مورد نظر

    if data == "MyAccount":
            await app.edit_message_text(chat_id, m_id, "اطلاعات حساب کاربری شما در Tac Self به شرح زیر می باشد:", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="👤نام شما", callback_data="text"),
                        InlineKeyboardButton(text=f"{call.from_user.first_name}", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text="🔖 آیدی شما", callback_data="text"),
                        InlineKeyboardButton(text=f"{call.from_user.id}", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text="📄 یوزرنیم شما", callback_data="text"),
                        InlineKeyboardButton(text=f"{username}", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text="💲موجودی شما", callback_data="text"),
                        InlineKeyboardButton(text=f"{amount} تومان", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text="⚙️وضعیت حساب شما", callback_data="text"),
                        InlineKeyboardButton(text=f"{account_status}", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text="𝒹𝒶𝓇𝓀℘𝓊ℓ𝓈", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text=f"انقضای شما ({expir}) روز", callback_data="text")
                    ],
                    [
                        InlineKeyboardButton(text="برگشت", callback_data="Back")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "BuySub" or data == "Back2":
        if user["phone"] is None:
            await app.delete_messages(chat_id, m_id)
            await app.send_message(chat_id, f"{get_random_emoji()} لطفا با استفاده از دکمه زیر شماره خود را به اشتراک بگذارید", reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(text=f"{get_random_emoji()} اشتراک گذاری شماره", request_contact=True)
                    ]
                ],resize_keyboard=True
            ))
            update_data(f"UPDATE user SET step = 'contact' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            if user["account"] == "verified":
                if not os.path.isfile(f"sessions/{chat_id}.session-journal"):
                    await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} مدت زمان اشتراک را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} 1 ماهه معادل 20000 تومان", callback_data="Login-30-20000")
                            ],
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} 2 ماهه معادل 45000 تومان", callback_data="Login-60-45000")
                            ],
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} 3 ماهه معادل 65000 تومان", callback_data="Login-90-65000")
                            ],
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} 4 ماهه معادل 85000 تومان", callback_data="Login-120-85000")
                            ],
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} 5 ماهه معادل 110000 تومان", callback_data="Login-150-110000")
                            ],
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} 6 ماهه معادل 130000 تومان", callback_data="Login-180-130000")
                            ],
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                            ]
                        ]
                    ))
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                    async with lock:
                        if chat_id in temp_Client:
                            del temp_Client[chat_id]
                    if os.path.isfile(f"sessions/{chat_id}.session") and not os.path.isfile(f"sessions/{chat_id}.session-journal"):
                        os.remove(f"sessions/{chat_id}.session")
                else:
                    await app.answer_callback_query(call.id, text=f"{get_random_emoji()} اشتراک سلف برای شما فعال است!", show_alert=True)
            else:
                await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} برای خرید اشتراک ابتدا باید احراز هویت کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} احراز هویت", callback_data="AccVerify")
                        ],
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data.split("-")[0] == "Login":
        expir_count = data.split("-")[1]
        cost = data.split("-")[2]
        if int(amount) >= int(cost):
            mess = await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} در حال پردازش...")
            async with lock:
                if chat_id not in temp_Client:
                    temp_Client[chat_id] = {}
                temp_Client[chat_id]["client"] = Client(f"sessions/{chat_id}", api_id=API_ID, api_hash=API_HASH, device_model="Maximusboy-SELF", system_version="Linux")
                temp_Client[chat_id]["number"] = phone_number
                await temp_Client[chat_id]["client"].connect()
            try:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} کد تایید 5 رقمی را با فرمت زیر ارسال کنید:\n1.2.3.4.5", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                async with lock:
                    temp_Client[chat_id]["response"] = await temp_Client[chat_id]["client"].send_code(temp_Client[chat_id]["number"])
                update_data(f"UPDATE user SET step = 'login1-{expir_count}-{cost}' WHERE id = '{call.from_user.id}' LIMIT 1")

            except errors.BadRequest:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} اتصال ناموفق بود! لطفا دوباره تلاش کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")

            except errors.PhoneNumberInvalid:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} این شماره نامعتبر است!", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")

            except errors.PhoneNumberBanned:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} این اکانت محدود است!", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat.id}.session")

            except Exception:
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
        else:
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} موجودی حساب شما برای خرید این اشتراک کافی نیست", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} افزایش موجودی", callback_data="Wallet")
                    ],
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Price":
        price_text = f"""
{get_random_emoji()} بَهاء سلف عبارت است از: 

{get_random_emoji()} » 1 ماهه: 20000 تومان
{get_random_emoji()} » 2 ماهه: 45000 تومان
{get_random_emoji()} » 3 ماهه: 65000 تومان
{get_random_emoji()} » 4 ماهه: 85000 تومان
{get_random_emoji()} » 5 ماهه: 110000 تومان
{get_random_emoji()} » 6 ماهه: 130000 تومان
"""
        await app.edit_message_text(chat_id, m_id, price_text, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Wallet" or data == "Back3":
        wallet_text = f"""
{get_random_emoji()} کیف پول شما:

{get_random_emoji()} موجودی: {amount} تومان

{get_random_emoji()} یکی از گزینه های زیر را انتخاب کنید:
"""
        await app.edit_message_text(chat_id, m_id, wallet_text, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} خرید موجودی", callback_data="BuyAmount"),
                    InlineKeyboardButton(text=f"{get_random_emoji()} انتقال موجودی", callback_data="TransferAmount")
                ],
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} استفاده از کد هدیه", callback_data="UseGiftCode")
                ],
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
    
    elif data == "BuyAmount":
        if user["account"] == "verified":
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} میزان موجودی مورد نظر خود را برای شارژ حساب وارد کنید:\nحداقل موجودی قابل خرید 10000 تومان است!", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'buyamount1' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} برای خرید موجودی ابتدا باید احراز هویت کنید", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} احراز هویت", callback_data="AccVerify")
                    ],
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
    
    elif data == "UseGiftCode":
        await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} لطفا کد هدیه خود را وارد کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'usegiftcode' WHERE id = '{call.from_user.id}' LIMIT 1")
    
    elif data.split("-")[0] == "AcceptAmount":
        user_id = int(data.split("-")[1])
        count = int(data.split("-")[2])
        user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
        user_upamount = int(user_amount["amount"]) + int(count)
        update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} تایید انجام شد\nمبلغ {count} تومان به حساب کاربر [ {user_id} ] انتقال یافت\nموجودی جدید کاربر: {user_upamount} تومان")
        await app.send_message(user_id, f"{get_random_emoji()} درخواست شما برای افزایش موجودی تایید شد\nمبلغ {count} تومان به حساب شما انتقال یافت\nموجودی جدید شما: {user_upamount} تومان")
    
    elif data.split("-")[0] == "RejectAmount":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} درخواست کاربر مورد نظر برای افزایش موجودی رد شد")
        await app.send_message(user_id, f"{get_random_emoji()} درخواست شما برای افزایش موجودی رد شد")
    
    elif data == "TransferAmount":
        if user["account"] == "verified":
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} آیدی عددی کاربری که قصد انتقال موجودی به او را دارید ارسال کنید:", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'transferam1' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} برای انتقال موجودی ابتدا باید احراز هویت کنید", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} احراز هویت", callback_data="AccVerify")
                    ],
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
    
    elif data == "AccVerify":
        if user["account"] != "verified":
            verify_text = f"""
{get_random_emoji()} به بخش احراز هویت خوش آمدید.
{get_random_emoji()} نکات:
1) شماره کارت و نام صاحب کارت کاملا مشخص باشد.
2) لطفا تاریخ اعتبار و Cvv2 کارت خود را بپوشانید!
3) اسکرین شات و عکس از کارت از داخل موبایل بانک قابل قبول نیستند
4) فقط با کارتی که احراز هویت میکنید میتوانید خرید انجام بدید و اگر با کارت دیگری اقدام کنید تراکنش ناموفق میشود و هزینه از سمت خودِ بانک به شما بازگشت داده میشود.
5) در صورتی که توانایی ارسال عکس از کارت را ندارید تنها راه حل ارسال عکس از کارت ملی یا شناسنامه صاحب کارت است.

{get_random_emoji()} لطفا عکس از کارتی که میخواهید با آن خرید انجام دهید ارسال کنید.
"""
            await app.edit_message_text(chat_id, m_id, verify_text, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'accverify' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            await app.answer_callback_query(call.id, f"{get_random_emoji()} حساب شما تایید شده است!", show_alert=True)
    
    elif data.split("-")[0] == "AcceptVerify":
        user_id = int(data.split("-")[1])
        update_data(f"UPDATE user SET account = 'verified' WHERE id = '{user_id}' LIMIT 1")
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} حساب کاربر [ {user_id} ] تایید شد")
        await app.send_message(user_id, f"{get_random_emoji()} حساب کاربری شما تایید شد و اکنون می توانید بدون محدودیت از ربات استفاده کنید")
    
    elif data.split("-")[0] == "RejectVerify":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} درخواست کاربر مورد نظر برای تایید حساب کاربری رد شد")
        await app.send_message(user_id, f"{get_random_emoji()} درخواست شما برای تایید حساب کاربری رد شد")

    elif data == "Subinfo" or data == "Back4":
        if os.path.isfile(f"sessions/{chat_id}.session-journal"):
            substatus = "فعال" if user["self"] == "active" else "غیرفعال"
            subinfo_text = f"""
{get_random_emoji()} وضعیت اشتراک: {substatus}
{get_random_emoji()} شماره تلفن: {phone_number}
{get_random_emoji()} انقضا: {expir} روز
{get_random_emoji()} تاریخ انقضا: {expiration_date_str}
"""
            await app.edit_message_text(chat_id, m_id, subinfo_text, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} خرید انقضا", callback_data="BuyExpir"),
                        InlineKeyboardButton(text=f"{get_random_emoji()} انتقال انقضا", callback_data="TransferExpir")
                    ],
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                    ]
                ]
            ))
        else:
            await app.answer_callback_query(call.id, text=f"{get_random_emoji()} شما اشتراک فعالی ندارید!", show_alert=True)
    
    elif data == "BuyExpir":
        if user["account"] == "verified":
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} میزان انقضای مورد نظر خود را برای افزایش وارد کنید:\nهزینه هر یک روز انقضا 1000 تومان است", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back4")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'buyexpir1' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} برای خرید انقضا ابتدا باید احراز هویت کنید", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} احراز هویت", callback_data="AccVerify")
                    ],
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back4")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
    
    elif data.split("-")[0] == "AcceptExpir":
        user_id = int(data.split("-")[1])
        count = int(data.split("-")[2])
        user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
        user_upexpir = int(user_expir["expir"]) + int(count)
        update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} تایید انجام شد\n{count} روز به انقضای کاربر [ {user_id} ] افزوده شد\nانقضای جدید کاربر: {user_upexpir} روز")
        await app.send_message(user_id, f"{get_random_emoji()} درخواست شما برای افزایش انقضا تایید شد\n{count} روز به انقضای شما افزوده شد\nانقضای جدید شما: {user_upexpir} روز")
    
    elif data.split("-")[0] == "RejectExpir":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} درخواст کاربر مورد نظر برای افزایش انقضا رد شد")
        await app.send_message(user_id, f"{get_random_emoji()} درخواست شما برای افزایش انقضا رد شد")

    elif data == "TransferExpir":
        if user["account"] == "verified":
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} آیدی عددی کاربری که قصد انتقال انقضا به او را دارید ارسال کنید:", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back4")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'transferex1' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} برای انتقال انقضا ابتدا باید احراز هویت کنید", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} احراز هویت", callback_data="AccVerify")
                    ],
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back4")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "WhatSelf":
        whatself_text = f"""
{get_random_emoji()} سلف به رباتی گفته میشه که روی اکانت شما نصب میشه و امکانات خاصی رو در اختیارتون میزاره ، لازم به ذکر هست که نصب شدن بر روی اکانت شما به معنی وارد شدن ربات به اکانت شما هست ( به دلیل دستور گرفتن و انجام فعالیت ها )
{get_random_emoji()} از جمله امکاناتی که در اختیار شما قرار میدهد شامل موارد زیر است:

{get_random_emoji()} گذاشتن ساعت با فونت های مختلف بر روی بیو ، اسم
{get_random_emoji()} قابلیت تنظیم حالت خوانده شدن خودکار پیام ها
{get_random_emoji()} تنظیم حالت پاسخ خودکار
{get_random_emoji()} پیام انیمیشنی
{get_random_emoji()} منشی هوشمند
{get_random_emoji()} دریافت پنل و تنظیمات اکانت هوشمند
{get_random_emoji()} دو زبانه بودن دستورات و جواب ها
{get_random_emoji()} تغییر نام و کاور فایل ها
{get_random_emoji()} اعلان پیام ادیت و حذف شده در پیوی
{get_random_emoji()} ذخیره پروفایل های جدید و اعلان حذف پروفایل مخاطبین

{get_random_emoji()} و امکاناتی دیگر که میتوانید با مراجعه به بخش راهنما آن ها را ببینید و مطالعه کنید!

{get_random_emoji()} لازم به ذکر است که امکاناتی که در بالا گفته شده تنها ذره ای از امکانات سلف میباشد .
"""
        await app.edit_message_text(chat_id, m_id, whatself_text, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Support":
        await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} پیام خود را ارسال کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'support' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "GiftCode":
        await app.edit_message_text(chat_id, m_id, f"{get_random_emoji()} برای استفاده از کد هدیه، آن را در قسمت زیر وارد کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} استفاده از ک드 هدیه", callback_data="UseGiftCode")
                ],
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data.split("-")[0] == "Reply":
        exit = data.split("-")[1]
        getuser = await app.get_users(exit)
        await app.send_message(Admin, f"{get_random_emoji()} پیام خود را برای کاربر [ {html.escape(getuser.first_name)} ] ارسال کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} صفحه اصلی", callback_data="Back"),
                    InlineKeyboardButton(text=f"{get_random_emoji()} پنل مدیریت", callback_data="Panel")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'ureply-{exit}' WHERE id = '{Admin}' LIMIT 1")

    elif data.split("-")[0] == "Block":
        exit = data.split("-")[1]
        getuser = await app.get_users(exit)
        block = get_data(f"SELECT * FROM block WHERE id = '{exit}' LIMIT 1")
        if block is None:
            await app.send_message(exit, f"{get_random_emoji()} کاربر محترم شما به دلیل نقض قوانین از ربات مسدود شدید")
            await app.send_message(Admin, f"{get_random_emoji()} کاربر [ {html.escape(getuser.first_name)} ] از ربات بلاک شد")
            update_data(f"INSERT INTO block(id) VALUES({exit})")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} کاربر [ {html.escape(getuser.first_name)} ] از قبل بلاک است")

    elif data == "Back":
        welcome_text = f"""
{get_random_emoji()} سلام کاربر {html.escape(call.from_user.first_name)} {get_random_emoji()}
به سلف ساز Dark Pulse خوش آمدید! {get_random_emoji()}

{get_random_emoji()} اینجا میتونی سلف خودت رو بسازی و مدیریت کنی
{get_random_emoji()} از امکانات ویژه ربات استفاده کنی
{get_random_emoji()} و کلی کارهای جالب دیگه انجام بدی!

لطفا از منوی زیر گزینه مورد نظرت رو انتخاب کن:
"""
        await app.edit_message_text(chat_id, m_id, welcome_text, reply_markup=Main)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
        async with lock:
            if chat_id in temp_Client:
                del temp_Client[chat_id]
    
    elif data == "text":
        await app.answer_callback_query(call.id, text=f"{get_random_emoji()} این دکمه نمایشی است", show_alert=True)

    # ==================== Admin Panel Callbacks =====================#
    elif data == "Panel":
        await app.send_message(Admin, f"{get_random_emoji()} مدیر گرامی به پنل مدیریت Dark Pulse خوش آمدید!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]
    
    elif data == "GiftCodePanel":
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} مدیریت کدهای هدیه", reply_markup=GiftCodePanel)
    
    elif data == "CreateGiftCode":
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} لطفا اطلاعات کد هدیه را به فرمت زیر ارسال کنید:\n\nمبلغ-تعداد روز-حداکثر استفاده\n\nمثال: 10000-30-5")
        update_data(f"UPDATE user SET step = 'creategiftcode' WHERE id = '{Admin}' LIMIT 1")
    
    elif data == "ListGiftCodes":
        codes = get_datas("SELECT * FROM gift_codes")
        if codes:
            codes_text = f"{get_random_emoji()} لیست کدهای هدیه:\n\n"
            for code in codes:
                codes_text += f"{get_random_emoji()} کد: {code[0]}\nمبلغ: {code[1]} تومان\nروز: {code[2]} روز\nاستفاده شده: {code[4]}/{code[3]}\n\n"
            await app.edit_message_text(Admin, m_id, codes_text, reply_markup=GiftCodePanel)
        else:
            await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} هیچ کد هدیه ای وجود ندارد", reply_markup=GiftCodePanel)
    
    elif data == "DeleteGiftCode":
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} لطفا کد هدیه ای که می خواهید حذف کنید را ارسال کنید:")
        update_data(f"UPDATE user SET step = 'deletegiftcode' WHERE id = '{Admin}' LIMIT 1")
    
    elif data == "BackToPanel":
        await app.send_message(Admin, f"{get_random_emoji()} مدیر گرامی به پنل مدیریت Dark Pulse خوش آمدید!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
    
    elif data == "ResetSelfs":
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} آیا مطمئن هستید که می خواهید سلف تمام کاربران را ریست کنید؟\n\nاین عمل فایل self.py در پوشه کاربران را با نسخه جدید جایگزین می کند.", reply_markup=ResetConfirm)
    
    elif data == "ConfirmReset":
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} در حال ریست سلف کاربران...")
        report = await reset_all_selfs()
        await app.send_message(Admin, f"{get_random_emoji()} گزارش ریست سلف:\n\n{report}", reply_markup=AdminPanel)
    
    elif data == "CancelReset":
        await app.send_message(Admin, f"{get_random_emoji()} مدیر گرامی به پنل مدیریت Dark Pulse خوش آمدید!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
    
    elif data.split("-")[0] == "DeleteSub":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} هشدار! با این کار اشتراک کاربر مورد نظر به طور کامل حذف می شود و امکان فعالسازی دوباره از پنل مدیریت وجود ندارد\n\nاگر از این کار اطمینان دارید روی گزینه تایید و در غیر این صورت روی گزینه برگشت کلیک کنید", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} تایید", callback_data=f"AcceptDelSub-{user_id}")
                ],
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="AdminBack")
                ]
            ]
        ))
    
    elif data.split("-")[0] == "AcceptDelSub":
        await app.edit_message_text(Admin, m_id, f"{get_random_emoji()} اشتراک سلف کاربر مورد نظر به طور کامل حذف شد", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="AdminBack")
                ]
            ]
        ))
        user_id = int(data.split("-")[1])
        if os.path.isdir(f"selfs/self-{user_id}"):
            shutil.rmtree(f"selfs/self-{user_id}")
        if os.path.isfile(f"sessions/{user_id}.session"):
            async with Client(f"sessions/{user_id}") as user_client:
                await user_client.log_out()
            if os.path.isfile(f"sessions/{user_id}.session"):
                os.remove(f"sessions/{user_id}.session")
        if os.path.isfile(f"sessions/{user_id}.session-journal"):
            os.remove(f"sessions/{user_id}.session-journal")
        update_data(f"UPDATE user SET expir = '0' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET pid = NULL WHERE id = '{user_id}' LIMIT 1")
        await app.send_message(user_id, f"{get_random_emoji()} کاربر گرامی اشتراک سلف شما توسط مدیر حذف شد\nبرای کسب اطلاعات بیشتر و دلیل حذف اشتراک به پشتیبانی مراجعه کنید")
    
    elif data == "AdminBack":
        await app.delete_messages(Admin, m_id)
        await app.send_message(Admin, f"{get_random_emoji()} مدیر گرامی به پنل مدیریت Dark Pulse خوش آمدید!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]

async def reset_all_selfs():
    report = ""
    users = get_datas("SELECT id FROM user WHERE self = 'active'")
    for user in users:
        user_id = user[0]
        try:
            # Kill the process
            user_data = get_data(f"SELECT pid FROM user WHERE id = '{user_id}' LIMIT 1")
            if user_data and user_data["pid"]:
                try:
                    os.kill(user_data["pid"], signal.SIGKILL)
                except:
                    pass

            # مسیر پوشه کاربر
            user_dir = f"selfs/self-{user_id}"

            # حذف فایل self.py فقط
            self_path = os.path.join(user_dir, "self.py")
            if os.path.isfile(self_path):
                os.remove(self_path)

            # استخراج فایل جدید فقط
            with zipfile.ZipFile("source/Self.zip", "r") as extract:
                extract.extract("self.py", path=user_dir)

            # راه‌اندازی مجدد
            process = subprocess.Popen(["python3", "self.py", str(user_id), str(API_ID), API_HASH, Helper_ID], cwd=user_dir)
            await asyncio.sleep(5)

            if process.poll() is None:
                update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{user_id}' LIMIT 1")
                report += f"{get_random_emoji()} کاربر {user_id}: موفق\n"
            else:
                report += f"{get_random_emoji()} کاربر {user_id}: خطا در راه‌اندازی\n"

        except Exception as e:
            report += f"{get_random_emoji()} کاربر {user_id}: خطا - {str(e)}\n"

    return report

async def toggle_selfs(action):
    report = ""
    users = get_datas("SELECT id FROM user WHERE self = 'active'")
    for user in users:
        user_id = user[0]
        try:
            user_data = get_data(f"SELECT pid FROM user WHERE id = '{user_id}' LIMIT 1")
            if user_data and user_data["pid"]:
                if action == "stop":
                    try:
                        os.kill(user_data["pid"], signal.SIGKILL)
                    except:
                        pass
                    report += f"{get_random_emoji()} کاربر {user_id}: متوقف شد\n"
                elif action == "start":
                    # Restart the self
                    if not os.path.isdir(f"selfs/self-{user_id}"):
                        os.mkdir(f"selfs/self-{user_id}")
                        with zipfile.ZipFile("source/Self.zip", "r") as extract:
                            extract.extractall(f"selfs/self-{user_id}")
                    
                    process = subprocess.Popen(["python3", "self.py", str(user_id), str(API_ID), API_HASH, Helper_ID], cwd=f"selfs/self-{user_id}")
                    await asyncio.sleep(5)
                    
                    if process.poll() is None:
                        update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{user_id}' LIMIT 1")
                        report += f"{get_random_emoji()} کاربر {user_id}: راه اندازی شد\n"
                    else:
                        report += f"{get_random_emoji()} کاربر {user_id}: خطا در راه اندازی\n"
            else:
                report += f"{get_random_emoji()} کاربر {user_id}: PID یافت نشد\n"
                
        except Exception as e:
            report += f"{get_random_emoji()} کاربر {user_id}: خطا - {str(e)}\n"
    
    return report

@app.on_message(filters.contact)
@checker
async def update(c, m):
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    if user["step"] == "contact":
        phone_number = str(m.contact.phone_number)
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
        contact_id = m.contact.user_id
        if m.contact and m.chat.id == contact_id:
            mess = await app.send_message(m.chat.id, f"{get_random_emoji()} شماره شما تایید شد", reply_markup=ReplyKeyboardRemove())
            update_data(f"UPDATE user SET phone = '{phone_number}' WHERE id = '{m.chat.id}' LIMIT 1")
            await asyncio.sleep(1)
            await app.delete_messages(m.chat.id, mess.id)
            welcome_text = f"""
{get_random_emoji()} سلام کاربر {html.escape(m.chat.first_name)} {get_random_emoji()}
به سلف ساز Dark Pulse خوش آمدید! {get_random_emoji()}

{get_random_emoji()} اینجا میتونی سلف خودت رو بسازی و مدیریت کنی
{get_random_emoji()} از امکانات ویژه ربات استفاده کنی
{get_random_emoji()} و کلی کارهای جالب دیگه انجام بدی!

لطفا از منوی زیر گزینه مورد نظرت رو انتخاب کن:
"""
            await app.send_message(m.chat.id, welcome_text, reply_markup=Main)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(m.chat.id, f"{get_random_emoji()} لطفا از دکمه اشتراک گذاری شماره استفاده کنید!")

@app.on_message(filters.private)
@checker
async def update(c, m):
    global temp_Client
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    username = f"@{m.from_user.username}" if m.from_user.username else "وجود ندارد"
    phone_number = user["phone"]
    expir = user["expir"]
    amount = user["amount"]
    chat_id = m.chat.id
    text = m.text
    m_id = m.id

    if user["step"].split("-")[0] == "login1":
        if re.match(r'^\d\.\d\.\d\.\d\.\d$', text):
            code = ''.join(re.findall(r'\d', text))
            expir_count = user["step"].split("-")[1]
            cost = user["step"].split("-")[2]

            mess = await app.send_message(chat_id, f"{get_random_emoji()} در حال پردازش...")
            try:
                async with lock:
                    await temp_Client[chat_id]["client"].sign_in(temp_Client[chat_id]["number"], temp_Client[chat_id]["response"].phone_code_hash, code)
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                mess = await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} لاگین با موفقیت انجام شد")
                mess = await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} در حال فعالسازی سلف...\n(ممکن است چند لحظه طول بکشد)")
                if not os.path.isdir(f"selfs/self-{m.chat.id}"):
                    os.mkdir(f"selfs/self-{m.chat.id}")
                    with zipfile.ZipFile("source/Self.zip", "r") as extract:
                        extract.extractall(f"selfs/self-{m.chat.id}")
                process = subprocess.Popen(["python3", "self.py", str(m.chat.id), str(API_ID), API_HASH, Helper_ID], cwd=f"selfs/self-{m.chat.id}")
                await asyncio.sleep(10)
                if process.poll() is None:
                    await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} سلف شما با موفقیت وصل به سرور ما شد\nمدت زمان اشتراک: {expir_count} روز", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                            ]
                        ]
                    ))
                    upamount = int(amount) - int(cost)
                    update_data(f"UPDATE user SET amount = '{upamount}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET expir = '{expir_count}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET self = 'active' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                    add_admin(m.chat.id)
                    await setscheduler(m.chat.id)
                    await app.send_message(Admin, f"{get_random_emoji()} گزارش خرید اشتراک\n\nآیدی کاربر: `{m.chat.id}`\nشماره کاربر: {phone_number}\nقیمت اشتراک: {cost} تومان\nمدت زمان اشتراک: {expir_count} روز")
                else:
                    await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} در فعالسازی سلف برای اکانت شما مشکلی رخ داد! هیچ مبلغی از حساب شما کسر نشد\nلطفا دوباره امتحان کنید و در صورتی که مشکل ادامه داشت با پشتیبانی تماس بگیرید", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                            ]
                        ]
                    ))
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                    if os.path.isfile(f"sessions/{chat_id}.session"):
                        os.remove(f"sessions/{chat_id}.session")

            except errors.SessionPasswordNeeded:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} رمز تایید دو مرحله ای برای اکانت شما فعال است\nرمز را وارد کنید:", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'login2-{expir_count}-{cost}' WHERE id = '{m.chat.id}' LIMIT 1")

            except errors.BadRequest:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} کد نامعتبر است!")
            except errors.PhoneCodeInvalid:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} کد نامعتبر است!")
            except errors.PhoneCodeExpired:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} کد منقضی شده است! لطفا عملیات ورود را دوباره تکرار کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
            
            except Exception:
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} فرمت نامعتبر است! لطفا کد را با فرمت ذکر شده وارد کنید:")
    
    elif user["step"].split("-")[0] == "login2":
        password = text.strip()
        expir_count = user["step"].split("-")[1]
        cost = user["step"].split("-")[2]

        mess = await app.send_message(chat_id, f"{get_random_emoji()} در حال پردازش...")
        try:
            async with lock:
                await temp_Client[chat_id]["client"].check_password(password)
                await temp_Client[chat_id]["client"].disconnect()
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
            mess = await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} لاگین با موفقیت انجام شد")
            mess = await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} در حال فعالسازی سلف...\n(ممکن است چند لحظه طول بکشد)")
            if not os.path.isdir(f"selfs/self-{m.chat.id}"):
                os.mkdir(f"selfs/self-{m.chat.id}")
                with zipfile.ZipFile("source/Self.zip", "r") as extract:
                    extract.extractall(f"selfs/self-{m.chat.id}")
            process = subprocess.Popen(["python3", "self.py", str(m.chat.id), str(API_ID), API_HASH, Helper_ID], cwd=f"selfs/self-{m.chat.id}")
            await asyncio.sleep(10)
            if process.poll() is None:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} سلف با موفقیت برای اکانت شما فعال شد\nمدت زمان اشترак: {expir_count} روز", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                        ]
                    ]
                ))
                upamount = int(amount) - int(cost)
                update_data(f"UPDATE user SET amount = '{upamount}' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET expir = '{expir_count}' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET self = 'active' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                add_admin(m.chat.id)
                await setscheduler(m.chat.id)
                await app.send_message(Admin, f"{get_random_emoji()} گزارش خرید اشتراک\n\n👤آیدی کاربر: {username}\n👀نام کاربر : {m.chat.first_name}\n💲قیمت اشتراک: {cost} تومان\n⏰مدت زمان اشتراک: {expir_count} روز")
            else:
                await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} در فعالسازی سلف برای اکانت شما مشکلی رخ داد! هیچ مبلغی از حساب شما کسر نشد\nلطفا دوباره امتحان کنید و در صورتی که مشکل ادامه داشت با پشتیبانی تماس بگیرید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")

        except errors.BadRequest:
            await app.edit_message_text(chat_id, mess.id, f"{get_random_emoji()} رمز نادرست است!\nرمز را وارد کنید:", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back2")
                    ]
                ]
            ))

        except Exception:
            async with lock:
                await temp_Client[chat_id]["client"].disconnect()
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
            if os.path.isfile(f"sessions/{chat_id}.session"):
                os.remove(f"sessions/{chat_id}.session")

    elif user["step"] == "buyamount1":
        if text.isdigit():
            count = text.strip()
            if int(count) >= 10000:
                await app.send_message(chat_id, f"{get_random_emoji()} فاکتور افزایش موجودی به مبلغ {count} تومان ایجاد شد\n\nشماره کارت: `{CardNumber}`\nبه نام {CardName}\nمبلغ قابل پرداخت: {count} تومان\n\nبعد از پرداخت رسید تراکنش را در همین قسمت ارسال کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'buyamount2-{count}' WHERE id = '{m.chat.id}' LIMIT 1")
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} حداقل موجودی قابل خرید 10000 تومان است!")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "buyamount2":
        if m.photo:
            count = int(user["step"].split("-")[1])
            mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
            await app.send_message(Admin, f"""
{get_random_emoji()} مدیر گرامی درخواست افزایش موجودی جدید دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم пользователя: {username}
مبلغ درخواستی کاربر: {count} تومان
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} تایید", callback_data=f"AcceptAmount-{chat_id}-{count}"),
                        InlineKeyboardButton(text=f"{get_random_emoji()} رد کردن", callback_data=f"RejectAmount-{chat_id}")
                    ]
                ]
            ))
            await app.send_message(chat_id, f"{get_random_emoji()} رسید تراکنش شما ارسال شد. لطفا منتظر تایید توسط مدیر باشید", reply_to_message_id=m_id)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عکس مجاز است")
    
    elif user["step"] == "transferam1":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if user_id != m.chat.id:
                    await app.send_message(chat_id, f"{get_random_emoji()} میزان موجودی مورد نظر خود را برای انتقال وارد کنید:\nحداقل موجودی قابل ارسال 10000 تومان است")
                    update_data(f"UPDATE user SET step = 'transferam2-{user_id}' WHERE id = '{m.chat.id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, f"{get_random_emoji()} شما نمی توانید به خودتان موجودی انتقال دهید!")
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif user["step"].split("-")[0] == "transferam2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = text.strip()
            if int(amount) >= int(count):
                if int(count) >= 10000:
                    user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
                    upamount = int(amount) - int(count)
                    user_upamount = int(user_amount["amount"]) + int(count)
                    update_data(f"UPDATE user SET amount = '{upamount}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
                    await app.send_message(chat_id, f"{get_random_emoji()} مبلغ {count} تومان از حساب شما کسر شد و به حساب کاربر [ {user_id} ] انتقال یافت\nموجودی جدید شما: {upamount} تومان", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back3")
                            ]
                        ]
                    ))
                    await app.send_message(user_id, f"{get_random_emoji()} مبلغ {count} تومان از حساب کاربر [ {m.chat.id} ] به حساب شما انتقال یافت\nموجودی جدید شما: {user_upamount} تومان")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, f"{get_random_emoji()} حداقل موجودی قابل ارسال 10000 تومان است!")
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} موجودی شما کافی نیست!")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"] == "accverify":
        if m.photo:
            mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
            await app.send_message(Admin, f"""
{get_random_emoji()} مدیر گرامی درخواست تایید حساب کاربری دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم کاربر: {username}
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} تایید", callback_data=f"AcceptVerify-{chat_id}"),
                        InlineKeyboardButton(text=f"{get_random_emoji()} رد کردن", callback_data=f"RejectVerify-{chat_id}")
                    ]
                ]
            ))
            await app.send_message(chat_id, f"{get_random_emoji()} درخواست شما برای تایید حساب کاربری ارسال شد. لطفا منتظر تایید توسط مدیر باشید", reply_to_message_id=m_id)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عکس مجاز است")

    elif user["step"] == "buyexpir1":
        if text.isdigit():
            count = int(text.strip())
            if int(count) > 0:
                await app.send_message(chat_id, f"{get_random_emoji()} فاکتور افزایش انقضا به مدت {count} روز ایجاد شد\n\nشماره کارت: `{CardNumber}`\nبه نام {CardName}\nمبلغ قابل پرداخت: {count*1000} تومان\n\nبعد از پرداخت رسید تراکنش را در همین قسمت ارسال کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back4")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'buyexpir2-{count}' WHERE id = '{m.chat.id}' LIMIT 1")
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} حداقل انقضای قابل خرید 1 روز است!")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "buyexpir2":
        if m.photo:
            count = int(user["step"].split("-")[1])
            mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
            await app.send_message(Admin, f"""
{get_random_emoji()} مدیر گرامی درخواست افزایش انقضای جدید دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم کاربر: {username}
تعداد روز های درخواستی کاربر: {count} روز
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} تایید", callback_data=f"AcceptExpir-{chat_id}-{count}"),
                        InlineKeyboardButton(text=f"{get_random_emoji()} رد کردن", callback_data=f"RejectExpir-{chat_id}")
                    ]
                ]
            ))
            await app.send_message(chat_id, f"{get_random_emoji()} رسید تراکنش شما ارسال شد. لطفا منتظر تایید توسط مدیر باشید", reply_to_message_id=m_id)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عکس مجاز است")
        
    elif user["step"] == "transferex1":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if user_id != m.chat.id:
                    if os.path.isfile(f"sessions/{user_id}.session-journal"):
                        await app.send_message(chat_id, f"{get_random_emoji()} میزان انقضای مورد نظر خود را برای انتقال وارد کنید:\nحداقل باید 10 روز انقضا برای شما باقی بماند!")
                        update_data(f"UPDATE user SET step = 'transferex2-{user_id}' WHERE id = '{m.chat.id}' LIMIT 1")
                    else:
                        await app.send_message(chat_id, f"{get_random_emoji()} اشتراک سلف برای این کاربر فعال نیست!")
                else:
                    await app.send_message(chat_id, f"{get_random_emoji()} شما نمی توانید به خودتان انقضا انتقال دهید!")
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif user["step"].split("-")[0] == "transferex2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = text.strip()
            if int(expir) >= int(count):
                if int(expir) - int(count) >= 10:
                    user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
                    upexpir = int(expir) - int(count)
                    user_upexpir = int(user_expir["expir"]) + int(count)
                    update_data(f"UPDATE user SET expir = '{upexpir}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
                    await app.send_message(chat_id, f"{get_random_emoji()} {count} روز از انقضای شما کسر شد و به کاربر [ {user_id} ] انتقال یافت\nانقضای جدید شما: {upexpir} روز", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back4")
                            ]
                        ]
                    ))
                    await app.send_message(user_id, f"{get_random_emoji()} {count} روز از انقضای کاربر [ {m.chat.id} ] به شما انتقال یافت\nانقضای جدید شما: {user_upexpir} روز")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, f"{get_random_emoji()} حداقل باید 10 روز انقضا برای شما باقی بماند!")
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} انقضای شما کافی نیست!")
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"] == "support":
        mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
        await app.send_message(Admin, f"""
{get_random_emoji()} مدیر گرامی پیام ارسال شده جدید دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم کاربر: {username}
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} پاسخ", callback_data=f"Reply-{chat_id}"),
                    InlineKeyboardButton(text=f"{get_random_emoji()} بلاک", callback_data=f"Block-{chat_id}")
                ]
            ]
        ))
        await app.send_message(chat_id, f"{get_random_emoji()} پیام شما ارسال شد و در اسرع وقت به آن پاسخ داده خواهد شد", reply_to_message_id=m_id)

    elif user["step"].split("-")[0] == "ureply":
        exit = user["step"].split("-")[1]
        mess = await app.copy_message(from_chat_id=Admin, chat_id=exit, message_id=m_id)
        await app.send_message(exit, f"{get_random_emoji()} کاربر گرامی پیام ارسال شده جدید از پشتیبانی دارید", reply_to_message_id=mess.id)
        await app.send_message(Admin, f"{get_random_emoji()} پیام شما ارسال شد پیام دیگری ارسال یا روی یکی از گزینه های زیر کلیک کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"{get_random_emoji()} صفحه اصلی", callback_data="Back"),
                    InlineKeyboardButton(text=f"{get_random_emoji()} پنل مدیریت", callback_data="Panel")
                ]
            ]
        ))
    
    elif user["step"] == "usegiftcode":
        code = text.strip().upper()
        gift_code = get_data(f"SELECT * FROM gift_codes WHERE code = '{code}' LIMIT 1")
        if gift_code:
            if gift_code["used_count"] < gift_code["max_uses"]:
                # Check if user has already used this code
                used = get_data(f"SELECT * FROM used_gift_codes WHERE id = '{chat_id}' AND code = '{code}' LIMIT 1")
                if not used:
                    # Apply gift code benefits
                    if gift_code["amount"] > 0:
                        new_amount = amount + gift_code["amount"]
                        update_data(f"UPDATE user SET amount = '{new_amount}' WHERE id = '{chat_id}' LIMIT 1")
                    
                    if gift_code["expir_days"] > 0:
                        new_expir = expir + gift_code["expir_days"]
                        update_data(f"UPDATE user SET expir = '{new_expir}' WHERE id = '{chat_id}' LIMIT 1")
                    
                    # Update gift code usage
                    update_data(f"UPDATE gift_codes SET used_count = used_count + 1 WHERE code = '{code}' LIMIT 1")
                    update_data(f"INSERT INTO used_gift_codes(id, code) VALUES({chat_id}, '{code}')")
                    
                    # Send success message
                    success_msg = f"{get_random_emoji()} کد هدیه با موفقیت اعمال شد!\n"
                    if gift_code["amount"] > 0:
                        success_msg += f"{get_random_emoji()} مبلغ {gift_code['amount']} تومان به حساب شما اضافه شد\n"
                    if gift_code["expir_days"] > 0:
                        success_msg += f"{get_random_emoji()} {gift_code['expir_days']} روز به اشتراک شما اضافه شد\n"
                    
                    await app.send_message(chat_id, success_msg, reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                            ]
                        ]
                    ))
                else:
                    await app.send_message(chat_id, f"{get_random_emoji()} شما قبلا از این کد هدیه استفاده کرده اید!", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                            ]
                        ]
                    ))
            else:
                await app.send_message(chat_id, f"{get_random_emoji()} این کد هدیه به پایان رسیده است!", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                        ]
                    ]
                ))
        else:
            await app.send_message(chat_id, f"{get_random_emoji()} کد هدیه نامعتبر است!", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=f"{get_random_emoji()} برگشت", callback_data="Back")
                    ]
                ]
            ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

# ==================== Admin Panel Messages ======================#
@app.on_message(filters.private & filters.user(Admin), group=1)
async def update(c, m):
    bot = get_data("SELECT * FROM bot")
    user = get_data(f"SELECT * FROM user WHERE id = '{Admin}' LIMIT 1")
    text = m.text
    m_id = m.id

    if text == "برگشت ↪️":
        await app.send_message(Admin, f"{get_random_emoji()} مدیر گرامی به پنل مدیریت Dark Pulse خوش آمدید!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]

    elif text == "آمار 📊":
        mess = await app.send_message(Admin, f"{get_random_emoji()} در حال دریافت اطلاعات...")
        botinfo = await app.get_me()
        allusers = get_datas("SELECT COUNT(id) FROM user")[0][0]
        allblocks = get_datas("SELECT COUNT(id) FROM block")[0][0]
        await app.edit_message_text(Admin, mess.id, f"""
{get_random_emoji()} تعداد کاربران ربات: {allusers}
{get_random_emoji()} تعداد کاربران بلاک شده: {allblocks}
--------------------------
{get_random_emoji()} نام ربات: {botinfo.first_name}
{get_random_emoji()} آیدی ربات: `{botinfo.id}`
{get_random_emoji()} یوزرنیم ربات: @{botinfo.username}
""")
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")

    elif text == "ارسال همگانی ✉️":
        await app.send_message(Admin, f"{get_random_emoji()} پیام خود را ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'sendall' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "sendall":
        mess = await app.send_message(Admin, f"{get_random_emoji()} در حال ارسال به همه کاربران...")
        users = get_datas(f"SELECT id FROM user")
        for user in users:
            await app.copy_message(from_chat_id=Admin, chat_id=user[0], message_id=m_id)
            await asyncio.sleep(0.1)
        await app.edit_message_text(Admin, mess.id, f"{get_random_emoji()} پیام شما برای همه کاربران ارسال شد")
    
    elif text == "فوروارد همگانی ✉️":
        await app.send_message(Admin, f"{get_random_emoji()} پیام خود را ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'forall' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "forall":
        mess = await app.send_message(Admin, f"{get_random_emoji()} در حال فوروارد به همه کاربران...")
        users = get_datas(f"SELECT id FROM user")
        for user in users:
            await app.forward_messages(from_chat_id=Admin, chat_id=user[0], message_ids=m_id)
            await asyncio.sleep(0.1)
        await app.edit_message_text(Admin, mess.id, f"{get_random_emoji()} پیام شما برای همه کاربران فوروارد شد")
    
    elif text == "بلاک کاربر 🚫":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری را که می خواهید بلاک کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'userblock' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "userblock":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
                if block is None:
                    await app.send_message(user_id, f"{get_random_emoji()} کاربر محترم شما به دلیل نقض قوانین از ربات مسدود شدید")
                    await app.send_message(Admin, f"{get_random_emoji()} کاربر [ {user_id} ] از ربات بلاک شد")
                    update_data(f"INSERT INTO block(id) VALUES({user_id})")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} این کاربر از قبل بلاک است")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "آنبلاک کاربر ✅️":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری را که می خواهید آنبلاک کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'userunblock' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "userunblock":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
                if block is not None:
                    await app.send_message(user_id, f"{get_random_emoji()} کاربر عزیز شما آنبلاک شدید و اکنون می توانید از ربات استفاده کنید")
                    await app.send_message(Admin, f"{get_random_emoji()} کاربر [ {user_id} ] از ربات آنبلاک شد")
                    update_data(f"DELETE FROM block WHERE id = '{user_id}' LIMIT 1")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} این کاربر از ربات بلاک نیست!")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "افزودن موجودی ➕":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید موجودی او را افزایش دهید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'amountinc' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "amountinc":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                await app.send_message(Admin, f"{get_random_emoji()} میزان موجودی مورد نظر خود را برای افزایش وارد کنید:")
                update_data(f"UPDATE user SET step = 'amountinc2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "amountinc2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
            user_upamount = int(user_amount["amount"]) + int(count)
            update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
            await app.send_message(user_id, f"{get_random_emoji()} مبلغ {count} تومان به حساب شما انتقال یافت\nموجودی جدید شما: {user_upamount} تومان")
            await app.send_message(Admin, f"{get_random_emoji()} مبلغ {count} تومان به حساب کاربر [ {user_id} ] افزوده شد\nموجودی جدید کاربر: {user_upamount} تومان")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "کسر موجودی ➖":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید موجودی او را کاهش دهید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'amountdec' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "amountdec":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                await app.send_message(Admin, f"{get_random_emoji()} میزان موجودی مورد نظر خود را برای کاهش وارد کنید:")
                update_data(f"UPDATE user SET step = 'amountdec2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "amountdec2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
            user_upamount = int(user_amount["amount"]) - int(count)
            update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
            await app.send_message(user_id, f"{get_random_emoji()} مبلغ {count} تومان از حساب شما کسر شد\nموجودی جدید شما: {user_upamount} تومان")
            await app.send_message(Admin, f"{get_random_emoji()} مبلغ {count} تومان از حساب کاربر [ {user_id} ] کسر شد\nموجودی جدید کاربر: {user_upamount} تومان")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "افزودن زمان اشتراک ➕":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید زمان اشتراک او را افزایش دهید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'expirinc' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "expirinc":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if os.path.isfile(f"sessions/{user_id}.session-journal"):
                    await app.send_message(Admin, f"{get_random_emoji()} میزان انقضای مورد نظر خود را برای افزایش وارد کنید:")
                    update_data(f"UPDATE user SET step = 'expirinc2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} اشتراک سلف برای این کاربر فعال نیست!")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "expirinc2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
            user_upexpir = int(user_expir["expir"]) + int(count)
            update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
            await app.send_message(user_id, f"{get_random_emoji()} {count} روز به انقضای شما افزوده شد\nانقضای جدید شما: {user_upexpir} روز")
            await app.send_message(Admin, f"{get_random_emoji()} {count} روز به انقضای کاربر [ {user_id} ] افزوده شد\nانقضای جدید کاربر: {user_upexpir} روز")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "کسر زمان اشتراک ➖":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید موجودی او را کاهش دهید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'expirdec' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "expirdec":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if os.path.isfile(f"sessions/{user_id}.session-journal"):
                    await app.send_message(Admin, f"{get_random_emoji()} میزان انقضای مورد نظر خود را برای کاهش وارد کنید:")
                    update_data(f"UPDATE user SET step = 'expirdec2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} اشتراک سلف برای این کاربر فعال نیست!")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "expirdec2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
            user_upexpir = int(user_expir["expir"]) - int(count)
            update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
            await app.send_message(user_id, f"{get_random_emoji()} {count} روز از انقضای شما کسر شد\nانقضای جدید شما: {user_upexpir} روز")
            await app.send_message(Admin, f"{get_random_emoji()} {count} روز از انقضای کاربر [ {user_id} ] کسر شد\nانقضای جدید کاربر: {user_upexpir} روز")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "فعال کردن سلف 🔵":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید سلف او را فعال کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'selfactive' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "selfactive":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if os.path.isfile(f"sessions/{user_id}.session-journal"):
                    user_data = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
                    if user_data["self"] != "active":
                        mess = await app.send_message(Admin, f"{get_random_emoji()} در حال پردازش...\n(ممکن است چند لحظه طول بکشد)")
                        process = subprocess.Popen(["python3", "self.py", str(user_id), str(API_ID), API_HASH, Helper_ID], cwd=f"selfs/self-{user_id}")
                        await asyncio.sleep(10)
                        if process.poll() is None:
                            await app.edit_message_text(Admin, mess.id, f"{get_random_emoji()} سلف با موفقیت برای این کاربر فعال شد")
                            update_data(f"UPDATE user SET self = 'active' WHERE id = '{user_id}' LIMIT 1")
                            update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{user_id}' LIMIT 1")
                            add_admin(user_id)
                            await setscheduler(user_id)
                            await app.send_message(user_id, f"{get_random_emoji()} سلف شما توسط مدیر فعال شد")
                        else:
                            await app.edit_message_text(Admin, mess.id, f"{get_random_emoji()} در فعالسازی سلف برای این کاربر مشکلی پیش آمد! لطفا دوباره تلاش کنید")
                    else:
                        await app.send_message(Admin, f"{get_random_emoji()} سلف از قبل برای این کاربر فعال است!")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} اشتراک سلف برای این کاربر فعال نیست!")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "غیرفعال کردن سلف 🔴":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید سلف او را غیرفعال کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'selfinactive' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "selfinactive":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if os.path.isfile(f"sessions/{user_id}.session-journal"):
                    user_data = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
                    if user_data["self"] != "inactive":
                        mess = await app.send_message(Admin, f"{get_random_emoji()} در حال پردازش...")
                        try:
                            os.kill(user_data["pid"], signal.SIGKILL)
                        except:
                            pass
                        await app.edit_message_text(Admin, mess.id, f"{get_random_emoji()} سلف با موفقیت برای این کاربر غیرفعال شد")
                        update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
                        if user_id != Admin:
                            delete_admin(user_id)
                        job = scheduler.get_job(str(user_id))
                        if job:
                            scheduler.remove_job(str(user_id))
                        await app.send_message(user_id, f"{get_random_emoji()} سلف شما توسط مدیر غیرفعال شد")
                    else:
                        await app.send_message(Admin, f"{get_random_emoji()} سلف از قبل برای این کاربر غیرفعال است!")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} اشتراک سلف برای این کاربر فعال نیست!")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
    
    elif text == "روشن کردن ربات 🔵":
        if bot["status"] != "ON":
            await app.send_message(Admin, f"{get_random_emoji()} ربات روشن شد")
            update_data(f"UPDATE bot SET status = 'ON' LIMIT 1")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ربات از قبل روشن است!")
    
    elif text == "خاموش کردن ربات 🔴":
        if bot["status"] != "OFF":
            await app.send_message(Admin, f"{get_random_emoji()} ربات خاموش شد")
            update_data(f"UPDATE bot SET status = 'OFF' LIMIT 1")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ربات از قبل خاموش است!")

    elif text == "مدیریت کدهای هدیه 🎁":
        await app.send_message(Admin, f"{get_random_emoji()} مدیریت کدهای هدیه", reply_markup=GiftCodePanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "creategiftcode":
        if re.match(r'^\d+-\d+-\d+$', text):
            parts = text.split('-')
            amount = int(parts[0])
            expir_days = int(parts[1])
            max_uses = int(parts[2])
            
            code = generate_gift_code()
            update_data(f"INSERT INTO gift_codes(code, amount, expir_days, max_uses) VALUES('{code}', {amount}, {expir_days}, {max_uses})")
            
            await app.send_message(Admin, f"{get_random_emoji()} کد هدیه ایجاد شد:\n\nکد: {code}\nمبلغ: {amount} تومان\nروز: {expir_days} روز\nحداکثر استفاده: {max_uses} بار", reply_markup=AdminPanel)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} فرمت نامعتبر! لطفا به فرمت زیر ارسال کنید:\nمبلغ-تعداد روز-حداکثر استفاده\n\nمثال: 10000-30-5")
    
    elif user["step"] == "deletegiftcode":
        code = text.strip().upper()
        gift_code = get_data(f"SELECT * FROM gift_codes WHERE code = '{code}' LIMIT 1")
        if gift_code:
            update_data(f"DELETE FROM gift_codes WHERE code = '{code}' LIMIT 1")
            update_data(f"DELETE FROM used_gift_codes WHERE code = '{code}'")
            await app.send_message(Admin, f"{get_random_emoji()} کد هدیه {code} با موفقیت حذف شد", reply_markup=AdminPanel)
        else:
            await app.send_message(Admin, f"{get_random_emoji()} کد هدیه یافت نشد!", reply_markup=AdminPanel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
    
    elif text == "ریست سلف کاربران 🔄":
        await app.send_message(Admin, f"{get_random_emoji()} آیا مطمئن هستید که می خواهید سلف تمام کاربران را ریست کنید؟\n\nاین عمل فایل self.py در پوشه کاربران را با نسخه جدید جایگزین می کند.", reply_markup=ResetConfirm)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
    
    elif text == "حذف کامل سلف کاربر ❌":
        await app.send_message(Admin, f"{get_random_emoji()} آیدی عددی کاربری که می خواهید سلف او را کاملا حذف کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'deleteself' WHERE id = '{Admin}' LIMIT 1")
    
    elif user["step"] == "deleteself":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if os.path.isfile(f"sessions/{user_id}.session-journal"):
                    user_data = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
                    if user_data["self"] == "active":
                        try:
                            os.kill(user_data["pid"], signal.SIGKILL)
                        except:
                            pass
                    
                    # Remove directory and files
                    if os.path.isdir(f"selfs/self-{user_id}"):
                        shutil.rmtree(f"selfs/self-{user_id}")
                    if os.path.isfile(f"sessions/{user_id}.session"):
                        os.remove(f"sessions/{user_id}.session")
                    if os.path.isfile(f"sessions/{user_id}.session-journal"):
                        os.remove(f"sessions/{user_id}.session-journal")
                    
                    # Update database
                    update_data(f"UPDATE user SET expir = '0' WHERE id = '{user_id}' LIMIT 1")
                    update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
                    update_data(f"UPDATE user SET pid = NULL WHERE id = '{user_id}' LIMIT 1")
                    
                    if user_id != Admin:
                        delete_admin(user_id)
                    
                    job = scheduler.get_job(str(user_id))
                    if job:
                        scheduler.remove_job(str(user_id))
                    
                    await app.send_message(Admin, f"{get_random_emoji()} سلف کاربر [ {user_id} ] به طور کامل حذف شد")
                    await app.send_message(user_id, f"{get_random_emoji()} کاربر گرامی اشتراک سلف شما توسط مدیر حذف شد\nبرای کسب اطلاعات بیشتر و دلیل حذف اشتراک به پشتیبانی مراجعه کنید")
                else:
                    await app.send_message(Admin, f"{get_random_emoji()} اشتراک سلف برای این کاربر فعال نیست!")
            else:
                await app.send_message(Admin, f"{get_random_emoji()} چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, f"{get_random_emoji()} ورودی نامعتبر! فقط ارسال عدد مجاز است")
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")

    elif text == "صفحه اصلی 🏠":
        mess = await app.send_message(Admin, f"{get_random_emoji()} به صفحه اصلی برگشتید", reply_markup=ReplyKeyboardRemove())
        welcome_text = f"""
{get_random_emoji()} سلام کاربر {m.chat.first_name} {get_random_emoji()}
به سلف ساز Dark Pulse خوش آمدید! {get_random_emoji()}

{get_random_emoji()} اینجا میتونی سلف خودت رو بسازی و مدیریت کنی
{get_random_emoji()} از امکانات ویژه ربات استفاده کنی
{get_random_emoji()} و کلی کارهای جالب دیگه انجام بدی!

لطفا از منوی زیر گزینه مورد نظرت رو انتخاب کن:
"""
        await app.send_message(Admin, welcome_text, reply_markup=Main)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]
        await asyncio.sleep(1)
        await app.delete_messages(Admin, mess.id)

# ==================== Run ===================#
app.start(), print(Fore.YELLOW+"Started..."+Style.RESET_ALL), idle(), app.stop()