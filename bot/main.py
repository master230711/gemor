import telebot
from telebot import types
import requests
import pyfiglet
import html
import logging
import random
import ipaddress
import time
from datetime import datetime
from faker import Faker
import re
from telebot.apihelper import ApiException
import os
import platform
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import UserProfilePhoto
import asyncio
import webbrowser
from bs4 import BeautifulSoup
import config 
from telethon.tl.functions.users import GetFullUserRequest
import sqlite3
import threading

NUMVERIFY_API_KEY = config.NUMVERIFY
IPINFO_TOKEN = config.IPINFO
VK_TOKEN = config.VK
BOT_TOKEN = config.BOT_TOKEN
DB_FILE = 'users.db'
ADMIN_IDS = config.ADMIN
VK_API_URL = 'https://api.vk.com/method/users.get'
ADMIN_ID = config.ADMIN_R
CHANNEL_USERNAME = config.CHANNEL_USERNAME
API_ID = config.API_ID
PROTECTED_USERS = config.PROTECTED_USERS
API_HASH = config.API_HASH


client = TelegramClient('bot_session', API_ID, API_HASH)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def get_user_info(identifier):
    async with client:
        try:
            if identifier.isdigit():
                user = await client(GetFullUserRequest(int(identifier)))
            else:
                if identifier.startswith('@'):
                    identifier = identifier[1:]
                user = await client(GetFullUserRequest(identifier))
            return user.users[0] if user.users else None
        except Exception as e:
            return None

def run_async(coroutine):
    return loop.run_until_complete(coroutine)

def show_progress_bar(chat_id):
    progress_message = bot.send_message(chat_id, "Поиск информации... 0%")
    for i in range(10, 101, 10):
        bot.edit_message_text(f"Поиск информации... {i}%", chat_id, progress_message.message_id)
        time.sleep(0.5)
    bot.delete_message(chat_id, progress_message.message_id)

def show_progress_bar1(chat_id):
    progress_message = bot.send_message(chat_id, "Поиск информации... 0%")
    for i in range(10, 101, 10):
        bot.edit_message_text(f"Создание баннера... {i}%", chat_id, progress_message.message_id)
        time.sleep(0.5)
    bot.delete_message(chat_id, progress_message.message_id)

def show_progress_bar123(chat_id):
    progress_message = bot.send_message(chat_id, "Поиск информации... 0%")
    for i in range(10, 101, 10):
        bot.edit_message_text(f"Генерация... {i}%", chat_id, progress_message.message_id)
        time.sleep(0.5)
    bot.delete_message(chat_id, progress_message.message_id)

def fetch_phoneradar_info(phone: str, chat_id) -> str:
    phoneradar_url = f'http://phoneradar.ru/phone/{phone}'
    try:
        response = requests.get(phoneradar_url, timeout=7)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            reviews = soup.find('div', class_='alert alert-danger').text.strip()
        except:
            reviews = soup.find('table', class_='table').text.strip()

        lines = [line for line in reviews.split('\n') if line.strip()]
        formatted_lines = [f"┣ {line}" for line in lines[:-1]]
        formatted_lines.append(f"┗ {lines[-1]}")
        formatted_reviews = '\n'.join(formatted_lines)

    except requests.exceptions.RequestException:
        formatted_reviews = 'Ошибка при получении данных с PhoneRadar.'

    return formatted_reviews

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, username TEXT, is_blocked INTEGER, block_time INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS admins
                  (user_id INTEGER PRIMARY KEY)''')
conn.commit()


def is_user_blocked(user_id):
    cursor.execute("SELECT is_blocked, block_time FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        is_blocked, block_time = result
        if is_blocked == 1:
            if block_time == 0 or block_time > int(time.time()):
                return True
    return False

def is_admin(user_id):
    cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def get_phone_info(phone_number, is_rf=False):
    if is_rf:
        url = f"https://htmlweb.ru/geo/api.php?json&telcod={phone_number}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        if isinstance(data, dict):
            country = data.get('country', {}).get('name', 'Неизвестно')
            lang = data.get('country', {}).get('lang', 'Неизвестно')
            region = data.get('region', {}).get('name', 'Неизвестно')
            city = data.get('city', 'Неизвестно')
            operator_info = data.get('0', {})
            operator = operator_info.get('oper', 'Неизвестно')
            latitude = operator_info.get('latitude', 'Неизвестно')
            longitude = operator_info.get('longitude', 'Неизвестно')
            mobile = operator_info.get('mobile', 'Неизвестно')
            s = fetch_phoneradar_info(phone_number)

            info = (
                f'''
📲Номер: {phone_number}
┣ Страна: {country}
┣ Регион: {region}
┣ Город: {city}
┣ Оператор: {operator}
┣ Широта: {latitude}
┣ Долгота: {longitude}
┣ Язык: {lang}
┗ Валид: {mobile}
📲Phoneradar:
{s}
🌐Cоциальные сети:
┣ Одноклассники: https://ok.ru/profile/{phone_number}
┣ ВКонтакте: https://vk.com/search?c%5Bq%5D={phone_number}&c%5Bsection%5D=people
┣ Telegramm: https://t.me/{phone_number}
┣ Facebook: https://www.facebook.com/search/top?q={phone_number}
┣ Instagram: https://www.instagram.com/{phone_number}
┣ Twitter: https://twitter.com/search?q={phone_number}
┣ Bing: https://www.bing.com/search?q={phone_number}
┣ Skype: https://www.skype.org/search?q={phone_number}
┗ WhatsApp: https://www.whatsapp.com/search?g={phone_number}
'''
            )
        else:
            info = "Ошибка: Некорректный ответ от API."
    else:
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone_number}&format=1"
        response = requests.get(url)
        data = response.json()

        if data.get("valid"):
            country = data.get("country_name", "Неизвестно")
            region = data.get("location", "Неизвестно")
            city = data.get("location", "Неизвестно")
            operator = data.get("carrier", "Неизвестно")
            latitude = data.get("latitude", "Неизвестно")
            longitude = data.get("longitude", "Неизвестно")
            lang = data.get("line_type", "Неизвестно")
            mobile = "Да" if data.get("line_type") == "mobile" else "Нет"

            info = (
                f'''
📲Номер: {phone_number}
┣ Страна: {country}
┣ Регион: {region}
┣ Город: {city}
┣ Оператор: {operator}
┣ Широта: {latitude}
┣ Долгота: {longitude}
┣ Язык: {lang}
┗ Валид: {mobile}
'''
            )
        else:
            info = "Номер телефона недействителен или информация недоступна."

    return info

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

init_db()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
    ]
)

def get_ip_info1(ip_address):
    url = f"https://ipinfo.io/{ip_address}?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Ошибка запроса: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")

logger = logging.getLogger(__name__)

fake = Faker('ru_RU')
bot = telebot.TeleBot(BOT_TOKEN)

def generate_ip(version=4):
    if version == 4:
        return ".".join(str(random.randint(0, 255)) for _ in range(4))
    elif version == 6:
        return ":".join(f"{random.randint(0, 65535):04x}" for _ in range(8))

def get_ip_info(ip):
    try:
        if "." in ip:
            ip_obj = ipaddress.IPv4Address(ip)
        else:
            ip_obj = ipaddress.IPv6Address(ip)
        info = {
            "IP": ip,
            "Version": ip_obj.version,
            "Type": "Public" if ip_obj.is_global else "Private",
            "Reserved": ip_obj.is_reserved,
            "Loopback": ip_obj.is_loopback,
            "Link Local": ip_obj.is_link_local,
            "Multicast": ip_obj.is_multicast,
        }
        return info
    except ValueError:
        return None

def format_ip_info(info):
    if not info:
        return "Некорректный IP-адрес."
    return (
        f"=== IP-адрес (IPv{info['Version']}) ===\n"
        f"IP: {info['IP']}\n"
        f"Type: {info['Type']}\n"
        f"Reserved: {info['Reserved']}\n"
        f"Loopback: {info['Loopback']}\n"
        f"Link Local: {info['Link Local']}\n"
        f"Multicast: {info['Multicast']}\n"
    )

def generate_person_data():
    full_name = fake.name()
    gender = "Мужчина" if fake.boolean() else "Женщина"
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=90)
    age = (datetime.now().date() - birthdate).days // 365

    card_number = fake.credit_card_number(card_type='visa')
    cvc = fake.credit_card_security_code(card_type='visa')
    card_expiry = fake.credit_card_expire()
    bank_name = fake.bank()
    iban = fake.iban()

    address = fake.address().replace("\n", ", ")
    email = fake.email()
    phone_number = fake.phone_number()

    job = fake.job()
    company = fake.company()
    position = job

    inn = fake.random_int(min=1000000000, max=9999999999)
    snils = fake.random_int(min=10000000000, max=99999999999)
    passport_series = fake.random_number(digits=4, fix_len=True)
    passport_number = fake.random_number(digits=6, fix_len=True)
    driver_license = fake.random_number(digits=10, fix_len=True)

    social_network = {
        "Facebook": fake.user_name(),
        "Instagram": fake.user_name(),
        "Twitter": fake.user_name(),
    }

    interests = [fake.word() for _ in range(3)]

    return (
        f"=== Личные данные ===\n"
        f"ФИО: {full_name}\n"
        f"Пол: {gender}\n"
        f"Дата рождения: {birthdate}\n"
        f"Возраст: {age}\n\n"
        f"=== Финансовые данные ===\n"
        f"Номер карты: {card_number}\n"
        f"CVC: {cvc}\n"
        f"Срок действия карты: {card_expiry}\n"
        f"Банк: {bank_name}\n"
        f"IBAN: {iban}\n\n"
        f"=== Контактные данные ===\n"
        f"Адрес: {address}\n"
        f"Email: {email}\n"
        f"Номер телефона: {phone_number}\n\n"
        f"=== Профессиональные данные ===\n"
        f"Профессия: {job}\n"
        f"Компания: {company}\n"
        f"Должность: {position}\n\n"
        f"=== Документы ===\n"
        f"ИНН: {inn}\n"
        f"СНИЛС: {snils}\n"
        f"Паспорт: {passport_series} {passport_number}\n"
        f"Водительские права: {driver_license}\n\n"
        f"=== Социальные сети ===\n"
        f"Facebook: {social_network['Facebook']}\n"
        f"Instagram: {social_network['Instagram']}\n"
        f"Twitter: {social_network['Twitter']}\n\n"
        f"=== Интересы ===\n"
        f"{', '.join(interests)}\n"
    )

def generate_combined_data():
    ipv4 = generate_ip(version=4)
    ipv4_info = get_ip_info(ipv4)
    ipv4_data = format_ip_info(ipv4_info)

    ipv6 = generate_ip(version=6)
    ipv6_info = get_ip_info(ipv6)
    ipv6_data = format_ip_info(ipv6_info)

    person_data = generate_person_data()

    combined_data = f"{ipv4_data}\n{ipv6_data}\n{person_data}"
    return combined_data

def check_subscription(user_id):
       try:
           chat_member = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
           return chat_member.status in ['member', 'administrator', 'creator']
       except Exception as e:
           logging.error(f"Ошибка при проверке подписки: {e}")
           return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if check_subscription(user_id):
        add_user(user_id)
        bot.reply_to(message, "Привет! Перед началом посмотри все команды /help")
        s = types.InlineKeyboardMarkup(row_width=2)
        sub_1 = types.InlineKeyboardButton(f"✅РЕЗЕРВНАЯ ССЫЛКА✅", url='https://gemorproject.github.io/gemor/')
        s.add(sub_1)
        sent = bot.send_message(message.chat.id, "⚡ ✅РЕЗЕРВНАЯ ССЫЛКА✅ ⚡", reply_markup=s)
        bot.pin_chat_message(message.chat.id, sent.message_id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID or is_admin(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        block_button = types.InlineKeyboardButton("Заблокировать", callback_data='block')
        unblock_button = types.InlineKeyboardButton("Разблокировать", callback_data='unblock')
        add_admin_button = types.InlineKeyboardButton("Добавить админа", callback_data='add_admin')
        remove_admin_button = types.InlineKeyboardButton("Удалить админа", callback_data='remove_admin')
        mailing_button = types.InlineKeyboardButton("Рассылка", callback_data='mailing')
        markup.add(block_button, unblock_button,mailing_button, add_admin_button, remove_admin_button)
        bot.send_message(message.chat.id, "Админ панель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'block':
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя для блокировки:")
        bot.register_next_step_handler(msg, process_block_user)
    elif call.data == 'unblock':
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя для разблокировки:")
        bot.register_next_step_handler(msg, unblock_user)
    elif call.data == 'add_admin':
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя, чтобы сделать его админом:")
        bot.register_next_step_handler(msg, add_admin)
    elif call.data == 'remove_admin':
        msg = bot.send_message(call.message.chat.id, "Введите ID админа, чтобы удалить его:")
        bot.register_next_step_handler(msg, remove_admin)
    elif call.data == 'mailing':
        msg = bot.send_message(call.message.chat.id, "Введите сообщение для рассылки:")
        bot.register_next_step_handler(msg, mailing)

def process_block_user(message):
    try:
        user_id = int(message.text)
        if user_id in PROTECTED_USERS:
            bot.send_message(message.chat.id, "Этот пользователь защищен от блокировки.")
            return
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (user_id, is_blocked, block_time) VALUES (?, ?, ?)",
                           (user_id, 0, 0))
            conn.commit()
        msg = bot.send_message(message.chat.id, "Введите время блокировки в днях (0 для бессрочной блокировки):")
        bot.register_next_step_handler(msg, lambda m: block_user(m, user_id))
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID пользователя. Введите число.")

def block_user(message, user_id):
    try:
        block_days = int(message.text)
        if block_days < 0:
            bot.send_message(message.chat.id, "Время блокировки не может быть отрицательным.")
            return

        if block_days == 0:
            block_timestamp = 0
            cursor.execute("UPDATE users SET is_blocked = 1, block_time = ? WHERE user_id = ?",
                           (block_timestamp, user_id))
            conn.commit()
            bot.send_message(message.chat.id, f"Пользователь {user_id} заблокирован навсегда.")
            try:
                bot.send_message(user_id, "Вы были заблокированы навсегда.")
            except Exception as e:
                print(f"Не удалось уведомить пользователя {user_id}: {e}")
        else:
            block_timestamp = int(time.time()) + block_days * 86400  # 86400 секунд в дне
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_timestamp))
            cursor.execute("UPDATE users SET is_blocked = 1, block_time = ? WHERE user_id = ?",
                           (block_timestamp, user_id))
            conn.commit()
            bot.send_message(message.chat.id, f"Пользователь {user_id} заблокирован до {unblock_date}.")
            try:
                bot.send_message(user_id, f"Вы были заблокированы до {unblock_date}.")
            except Exception as e:
                print(f"Не удалось уведомить пользователя {user_id}: {e}")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное время блокировки. Введите число.")

def unblock_user(message):
    try:
        user_id = int(message.text)
        cursor.execute("UPDATE users SET is_blocked = 0, block_time = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, f"Пользователь {user_id} разблокирован.")
        try:
            bot.send_message(user_id, "Вы были разблокированы.")
        except Exception as e:
            print(f"Не удалось уведомить пользователя {user_id}: {e}")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID пользователя. Введите число.")

def add_admin(message):
    try:
        user_id = int(message.text)
        if user_id in PROTECTED_USERS:
            bot.send_message(message.chat.id, "Этот пользователь защищен и не может быть админом.")
            return
        cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, f"Пользователь {user_id} добавлен в админы.")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID пользователя. Введите число.")

def remove_admin(message):
    try:
        user_id = int(message.text)
        if user_id in PROTECTED_USERS:
            bot.send_message(message.chat.id, "Этот пользователь защищен и не может быть разжалован.")
            return
        cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, f"Пользователь {user_id} удален из админов.")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID пользователя. Введите число.")

def mailing(message):
    text = message.text
    cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0 OR (block_time > 0 AND block_time < ?)", (int(time.time()),))
    users = cursor.fetchall()
    for user in users:
        try:
            bot.send_message(user[0], text, parse_mode='Markdown')
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user[0]}: {e}")
    bot.send_message(message.chat.id, "Рассылка завершена.")

def check_blocks():
    while True:
        try:
            current_time = int(time.time())
            cursor.execute("SELECT user_id FROM users WHERE is_blocked = 1 AND block_time > 0 AND block_time < ?", (current_time,))
            users_to_unblock = cursor.fetchall()
            for user in users_to_unblock:
                cursor.execute("UPDATE users SET is_blocked = 0, block_time = 0 WHERE user_id = ?", (user[0],))
                conn.commit()
                try:
                    bot.send_message(user[0], "Ваша блокировка истекла, и вы снова можете использовать бота.")
                except Exception as e:
                    print(f"Не удалось уведомить пользователя {user[0]}: {e}")
            time.sleep(60)
        except Exception as e:
            print(f"Ошибка в функции check_blocks: {e}")

@bot.message_handler(commands=['generate'])
def generate_data(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.")
        return
    combined_data = generate_combined_data()
    show_progress_bar123(message.chat.id)
    bot.reply_to(message, f"Сгенерированные данные:\n{combined_data}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "⛄ Команды:\n"
                                      "💻 /ip <ip> - Поиск по ip\n"
                                      "📲 /num <number> - Поиск по номеру телефона\n"
                                      "📨 /tg <@username или id> - Поиск по Telegram\n"
                                      "🔵 /vk <vk_id> - Поиск по VK\n"
                                      "👾 /generate - генерация данных\n"
                                      "🤖 /banner <name> - Создает баннер(English)\n"
                                      "📬 /pos <name> - Поиск по почте\n"
                                      "🎆 /admin - Админ панель\n"
                                
                                )

#поиск вк
@bot.message_handler(commands=['vk'])
def handle_vk_command(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.")
        return
    try:

        user_id = message.text.split()[1]

        params = {
            'user_ids': user_id,
            'fields': 'first_name,last_name,photo_200,city,country,bdate,status,occupation,followers_count,sex,relation',
            'access_token': VK_TOKEN,
            'v': '5.131'
        }

        response = requests.get(VK_API_URL, params=params).json()

        if 'response' in response:
            user_info = response['response'][0]
            vk_id = f"https://vk.com/id{user_id}"

            first_name = user_info.get('first_name', 'Не указано')
            last_name = user_info.get('last_name', 'Не указано')
            photo_url = user_info.get('photo_200', 'Фотография отсутствует')
            city = user_info.get('city', {}).get('title', 'Не указано')
            country = user_info.get('country', {}).get('title', 'Не указано')
            bdate = user_info.get('bdate', 'Не указано')
            status = user_info.get('status', 'Не указано')
            occupation = user_info.get('occupation', {}).get('name', 'Не указано')
            followers_count = user_info.get('followers_count', 'Не указано')
            sex = user_info.get('sex', 'Не указано')
            relation = user_info.get('relation', 'Не указано')

            sex_map = {1: 'Женский', 2: 'Мужской', 0: 'Не указано'}
            relation_map = {
                1: 'Не женат/Не замужем',
                2: 'Есть друг/Есть подруга',
                3: 'Помолвлен/Помолвлена',
                4: 'Женат/Замужем',
                5: 'Всё сложно',
                6: 'В активном поиске',
                7: 'Влюблён/Влюблена',
                8: 'В гражданском браке',
                0: 'Не указано'
            }
            sex = sex_map.get(sex, 'Не указано')
            relation = relation_map.get(relation, 'Не указано')

            reply = (
                f"🔵 Вк: {vk_id}\n"
                f"👤 Имя: {first_name}\n"
                f"👤 Фамилия: {last_name}\n"
                f"🌍 Город: {city}\n"
                f"🌍 Страна: {country}\n"
                f"🎂 Дата рождения: {bdate}\n"
                f"💬 Статус: {status}\n"
                f"💼 Род деятельности: {occupation}\n"
                f"👥 Подписчиков: {followers_count}\n"
                f"🚻 Пол: {sex}\n"
                f"💍 Семейное положение: {relation}\n"
                f"📸 Фото: {photo_url}"
            )
        elif 'error' in response:
            reply = response['error'].get('error_msg', 'Неизвестная ошибка VK API.')
        else:
            reply = "Пользователь не найден."
        show_progress_bar(message.chat.id)
        bot.send_message(message.chat.id, reply)
    except IndexError:
        bot.send_message(message.chat.id, "Используйте команду в формате: /vk <user_id>")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

#поиск по тг
@bot.message_handler(commands=['tg'])
def tg_command(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.")
        return
    try:
        show_progress_bar(message.chat.id)
        identifier = message.text.split()[1]
        user_info = run_async(get_user_info(identifier))
        if user_info:
            if identifier.isdigit():
                username = user_info.username
                if username:
                    bot.reply_to(message, f"Username пользователя с ID {identifier}: @{username}")
                else:
                    boti = f"tg://user?id={identifier}"
                    bot.reply_to(message, f"У пользователя с ID {identifier} нет username.\n🔓 Аккаунт [ТЫК]({boti})\n", parse_mode="Markdown")
            else:
                user_id = user_info.id
                bot.reply_to(message, f"ID пользователя {identifier}: {user_id}")
        else:
            boti = f"tg://user?id={identifier}"
            bot.reply_to(message, f"Пользователь '{identifier}' не найден.\n🔓 Аккаунт [ТЫК]({boti})\n", parse_mode="Markdown")
    except IndexError:
        bot.reply_to(message, "Используйте команду так: /tg <ID или @username>")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

#поиск ip
@bot.message_handler(commands=['ip'])
def handle_osint_ip(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.")
        return

    command_text = message.text
    ip_match = re.search(r'/ip\s+([\d\.]+)', command_text)
    
    if ip_match:
        ip_address = ip_match.group(1)
        ip_info = get_ip_info1(ip_address)
        
        if ip_info:
            response_text = (
                f"🏳IP: {ip_info['ip']}\n"
                f"🔐Страна: {ip_info.get('country', 'N/A')}\n"
                f"🌎Регион: {ip_info.get('region', 'N/A')}\n"
                f"🌏Город: {ip_info.get('city', 'N/A')}\n"
                f"🌍Широта и долгота: {ip_info.get('loc', 'N/A')}\n"
                f"🖥Провайдер: {ip_info.get('org', 'N/A')}"
            )
        else:
            response_text = "Не удалось получить информацию по этому IP-адресу."
    else:
        response_text = "Неправильный формат команды. Используй: /ip IP-адрес"
    show_progress_bar(message.chat.id)
    bot.reply_to(message, response_text)

@bot.message_handler(commands=['num'])
def handle_osint_num(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.")
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Пожалуйста, укажите номер телефона после команды /num.")
            return

        phone_number = args[1]
        is_rf = 'rf' in args

        show_progress_bar(message.chat.id)

        info = get_phone_info(phone_number, is_rf)
        bot.reply_to(message, info)

    except Exception as e:
        logging.error(f"Ошибка в обработчике сообщений: {e}")
        bot.reply_to(message, "Произошла внутренняя ошибка. Попробуйте позже.")

@bot.message_handler(commands=['banner'])
def send_banner(message):
    user_id = message.from_user.id
    if is_user_blocked(message.from_user.id):
        cursor.execute("SELECT block_time FROM users WHERE user_id = ?", (message.from_user.id,))
        block_time = cursor.fetchone()[0]
        if block_time == 0:
            bot.send_message(message.chat.id, "Вы заблокированы навсегда и не можете использовать бота.")
        else:
            unblock_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_time))
            bot.send_message(message.chat.id, f"Вы заблокированы до {unblock_date} и не можете использовать бота.")
        return
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота.")
        return
    try:
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message, "Используйте команду так: /banner {номер шрифта} {текст}")
            return
        
        font_number = int(command_parts[1])
        banner_text = command_parts[2]

        fonts = pyfiglet.FigletFont.getFonts()

        boti = "https://github.com/GemorProject/fonts-/blob/main/fonts.txt"

        if font_number < 0 or font_number >= len(fonts):
            bot.reply_to(message, f"Шрифт с номером {font_number} не найден.\nДоступно шрифтов: {len(fonts)}\nПосмотреть шрифты: [ТЫК]({boti})", parse_mode="Markdown")
            return

        show_progress_bar1(message.chat.id)
        selected_font = fonts[font_number]

        banner = pyfiglet.figlet_format(banner_text, font=selected_font)
        bot.reply_to(message, f"<pre>{banner}</pre>", parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

if __name__ == "__main__":
    while True:
        try:
            threading.Thread(target=check_blocks, daemon=True).start()
            logging.info("Запуск бота...")
            bot.polling(none_stop=True)
        except telebot.apihelper.ApiException as e:
            logging.error(f"Ошибка при подключении к Telegram API: {e}")
            logging.info("Повторная попытка через 10 секунд...")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Ошибка при запуске бота: {e}")
            break