import telebot
from telebot import types
import schedule
import time
import threading
from datetime import datetime, timedelta
import os
from flask import Flask

# --- НАЛАШТУВАННЯ ---
BOT_TOKEN = '8491054750:AAFBBVZOgFbJvbxbiYmJl6-VDRIohaCV8Do'
bot = telebot.TeleBot(BOT_TOKEN)

# Файл, де будуть зберігатися ID користувачів, які підписалися
SUBSCRIBERS_FILE = "subscribers.txt"
# Файл для збереження мов користувачів
LANGUAGES_FILE = "languages.txt"

# --- ПЕРЕКЛАДИ ---
translations = {
    "uk": {
        "welcome_new": "✅ **Привіт!** Я буду нагадувати тобі про дні народження нашої групи щоранку о 07:00.",
        "welcome_existing": "Ти вже підписаний на нагадування! 👌",
        "today_birthday": "Так! Сьогодні святкує: {name} 🎂",
        "no_birthday_today": "Сьогодні без тортів. Днів народження немає. zzz",
        "reminder": "🔔 **НАГАДУВАННЯ** 🔔\n\nСьогодні День народження святкує: **{name}**! 🎂\nНе забудь привітати!",
        "settings": "⚙️ Налаштування",
        "upcoming_birthdays": "📅 Найближчі дні народження",
        "language": "Мова",
        "language_changed": "Мову змінено на українську 🇺🇦",
        "upcoming_title": "📅 **Найближчі дні народження:**\n\n",
        "upcoming_item": "• {name} - {date} ({days} дн.)",
        "no_upcoming": "Найближчих днів народження немає.",
        "back": "Назад"
    },
    "en": {
        "welcome_new": "✅ **Hello!** I will remind you about birthdays in our group every morning at 07:00.",
        "welcome_existing": "You are already subscribed to reminders! 👌",
        "today_birthday": "Yes! Today celebrates: {name} 🎂",
        "no_birthday_today": "No cakes today. No birthdays. zzz",
        "reminder": "🔔 **REMINDER** 🔔\n\nToday's birthday: **{name}**! 🎂\nDon't forget to congratulate!",
        "settings": "⚙️ Settings",
        "upcoming_birthdays": "📅 Upcoming Birthdays",
        "language": "Language",
        "language_changed": "Language changed to English 🇬🇧",
        "upcoming_title": "📅 **Upcoming Birthdays:**\n\n",
        "upcoming_item": "• {name} - {date} ({days} days)",
        "no_upcoming": "No upcoming birthdays.",
        "back": "Back"
    }
}

# --- FLASK КЕЕП-АЛАЙВ СЕРВЕР ---
app = Flask('')

@app.route('/')
def home():
    return "Я работаю!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

# --- СПИСОК ДНІВ НАРОДЖЕННЯ (22 людини) ---
birthdays = {
    "25-06": {"uk": "Іван Гайтина", "en": "Ivan Gaitina"},
    "26-08": {"uk": "Світлана Гаращук", "en": "Svitlana Harashchuk"},
    "15-08": {"uk": "Андрій Главук", "en": "Andrii Hlavyuk"},
    "04-11": {"uk": "Ілля Голуб(Січний)", "en": "Ilya Golub (Sichnyi)"},
    "17-01": {"uk": "Анастісія Данілова", "en": "Anastasiia Danilova"},
    "14-02": {"uk": "Єшенко Максим", "en": "Yeshenko Maxim"},
    "27-10": {"uk": "Зданевич Дмитро", "en": "Zdanevich Dmytro"},
    "10-04": {"uk": "Вікторія Каменчук", "en": "Victoria Kamenchuk"},
    "05-02": {"uk": "Кашуба Мар'ян", "en": "Kashuba Marian"},
    "25-05": {"uk": "Лозицький Микола", "en": "Lozitsky Mykola"},
    "08-02": {"uk": "Лопоша Ярослав", "en": "Loposh Yaroslav"},
    "03-04": {"uk": "Опанащук Роман", "en": "Opanaschuk Roman"},
    "25-11": {"uk": "Смаглюк Іванна", "en": "Smagluch Ievanna"},
    "07-03": {"uk": "Сорочинський Юрій", "en": "Sorochinsky Yuriy"},
    "09-07": {"uk": "Стискун Іванна", "en": "Stiskun Ivanna"},
    "31-12": {"uk": "Микитка", "en": "Mikytka"},
    "18-02": {"uk": "Федас Ярослав", "en": "Fedas Yaroslav"},
    "11-03": {"uk": "Чмут Валентина", "en": "Chmut Valentina"},
    "26-05": {"uk": "чупринюк Владислав", "en": "Chupryniuk Vladyslav"},
    "12-06": {"uk": "Щебет Олександр", "en": "Shebet Oleksandr"},
    "12-09": {"uk": "Чучкевич Олександр(Грю)", "en": "Chuchkevych Oleksandr(Grо)"},
    "29-10": {"uk": "Ярмак Дмитро", "en": "Yarmak Dmytro"},
    # ... додавай інших сюди
}

# --- РОБОТА З ФАЙЛОМ ПІДПИСНИКІВ ---
def get_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"Помилка читання файлу підписників: {e}")
        return set()

def add_subscriber(chat_id):
    users = get_subscribers()
    if str(chat_id) not in users:
        try:
            with open(SUBSCRIBERS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{chat_id}\n")
            return True
        except Exception as e:
            print(f"Помилка запису в файл підписників: {e}")
            return False
    return False

# --- РОБОТА З МОВАМИ ---
def get_user_language(chat_id):
    if not os.path.exists(LANGUAGES_FILE):
        return "uk"  # За замовчуванням українська
    try:
        with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2 and parts[0] == str(chat_id):
                    return parts[1] if parts[1] in ["uk", "en"] else "uk"
    except Exception as e:
        print(f"Помилка читання файлу мов: {e}")
    return "uk"

def set_user_language(chat_id, language):
    if language not in ["uk", "en"]:
        return False
    try:
        languages = {}
        if os.path.exists(LANGUAGES_FILE):
            with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        languages[parts[0]] = parts[1]
        
        languages[str(chat_id)] = language
        
        with open(LANGUAGES_FILE, "w", encoding="utf-8") as f:
            for user_id, lang in languages.items():
                f.write(f"{user_id}:{lang}\n")
        return True
    except Exception as e:
        print(f"Помилка запису мови: {e}")
        return False

def t(key, lang, **kwargs):
    """Функція для отримання перекладу"""
    return translations.get(lang, translations["uk"]).get(key, key).format(**kwargs)

# --- ФУНКЦІЯ СТВОРЕННЯ КЛАВІАТУРИ ---
def create_main_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(t("upcoming_birthdays", lang), callback_data="upcoming"))
    keyboard.add(types.InlineKeyboardButton(t("settings", lang), callback_data="settings"))
    return keyboard

def create_settings_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    uk_text = "🇺🇦 Українська" if lang == "uk" else "🇺🇦 Ukrainian"
    en_text = "🇬🇧 English" if lang == "en" else "🇬🇧 Англійська"
    
    if lang == "uk":
        uk_text = "✅ " + uk_text
    else:
        en_text = "✅ " + en_text
    
    keyboard.add(types.InlineKeyboardButton(uk_text, callback_data="lang_uk"))
    keyboard.add(types.InlineKeyboardButton(en_text, callback_data="lang_en"))
    keyboard.add(types.InlineKeyboardButton(t("back", lang), callback_data="back"))
    return keyboard

# --- ОБРОБКА КОМАНД ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    lang = get_user_language(chat_id)
    
    if add_subscriber(chat_id):
        text = t("welcome_new", lang)
    else:
        text = t("welcome_existing", lang)
    
    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=create_main_keyboard(lang))

@bot.message_handler(commands=['check'])
def check_today(message):
    chat_id = message.chat.id
    lang = get_user_language(chat_id)
    today = datetime.now().strftime("%d-%m")
    
    if today in birthdays:
        name = birthdays[today][lang]
        bot.reply_to(message, t("today_birthday", lang, name=name))
    else:
        bot.reply_to(message, t("no_birthday_today", lang))

# --- ОБРОБКА CALLBACK ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    lang = get_user_language(chat_id)
    
    if call.data == "upcoming":
        upcoming = get_upcoming_birthdays(lang)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=upcoming,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard(lang)
        )
    elif call.data == "settings":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=t("settings", lang),
            reply_markup=create_settings_keyboard(lang)
        )
    elif call.data == "lang_uk":
        set_user_language(chat_id, "uk")
        new_lang = "uk"
        bot.answer_callback_query(call.id, t("language_changed", new_lang))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=t("settings", new_lang),
            reply_markup=create_settings_keyboard(new_lang)
        )
    elif call.data == "lang_en":
        set_user_language(chat_id, "en")
        new_lang = "en"
        bot.answer_callback_query(call.id, t("language_changed", new_lang))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=t("settings", new_lang),
            reply_markup=create_settings_keyboard(new_lang)
        )
    elif call.data == "back":
        lang = get_user_language(chat_id)
        text = t("welcome_existing", lang) if str(chat_id) in get_subscribers() else t("welcome_new", lang)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard(lang)
        )

# --- ФУНКЦІЯ ДЛЯ ЗНАХОДЖЕННЯ НАЙБЛИЖЧИХ ДНІВ НАРОДЖЕННЯ ---
def get_upcoming_birthdays(lang):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    upcoming_list = []
    
    for date_str, names in birthdays.items():
        day, month = map(int, date_str.split("-"))
        birthday = datetime(today.year, month, day)
        
        # Якщо день народження вже пройшов цього року, беремо наступний рік
        if birthday < today:
            birthday = datetime(today.year + 1, month, day)
        
        days_until = (birthday - today).days
        upcoming_list.append({
            "date": birthday,
            "days": days_until,
            "name": names[lang],
            "date_str": date_str
        })
    
    # Сортуємо за кількістю днів
    upcoming_list.sort(key=lambda x: x["days"])
    
    # Беремо перші 3
    upcoming_list = upcoming_list[:3]
    
    if not upcoming_list:
        return t("no_upcoming", lang)
    
    text = t("upcoming_title", lang)
    for item in upcoming_list:
        date_display = item["date"].strftime("%d.%m")
        text += t("upcoming_item", lang, name=item["name"], date=date_display, days=item["days"])
        text += "\n"
    
    return text

# --- ФУНКЦІЯ РОЗСИЛКИ ---
def send_birthday_message():
    today = datetime.now().strftime("%d-%m")
    
    if today in birthdays:
        users = get_subscribers()
        if not users:
            print("Немає підписників для розсилки.")
            return
        
        for user_id in users:
            try:
                lang = get_user_language(int(user_id))
                name = birthdays[today][lang]
                text = t("reminder", lang, name=name)
                bot.send_message(int(user_id), text, parse_mode="Markdown")
            except Exception as e:
                print(f"Не вдалося надіслати користувачу {user_id}: {e}")
    else:
        print(f"Сьогодні ({today}) тихо.")

# --- ЗАПУСК ПОТОКІВ ---
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Запускаємо Flask keep-alive сервер
    keep_alive()
    
    # Плануємо час розсилки о 07:00
    schedule.every().day.at("07:00").do(send_birthday_message)
    
    # Запускаємо планувальник в окремому потоці
    threading.Thread(target=schedule_checker, daemon=True).start()
    
    print("Бот запущений! Натисни /start у боті, щоб підписатися.")
    print("Keep-alive сервер працює на порту 8080")
    # Запускаємо самого бота (щоб він відповідав на повідомлення)
    bot.infinity_polling()
