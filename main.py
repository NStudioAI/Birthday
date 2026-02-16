import telebot
import schedule
import time
import threading
from datetime import datetime
import os
from flask import Flask

# --- НАЛАШТУВАННЯ ---
BOT_TOKEN = '8491054750:AAFBBVZOgFbJvbxbiYmJl6-VDRIohaCV8Do'
bot = telebot.TeleBot(BOT_TOKEN)

# Файл, де будуть зберігатися ID користувачів, які підписалися
SUBSCRIBERS_FILE = "subscribers.txt"

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
    "01-01": "Олександр",
    "17-02": "Марія (сьогодні для тесту)", # Зміни на реальні дати
    "24-08": "Іван",
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

# --- ОБРОБКА КОМАНД ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if add_subscriber(chat_id):
        bot.reply_to(message, "✅ **Привіт!** Я буду нагадувати тобі про дні народження нашої групи щоранку о 09:00.", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Ти вже підписаний на нагадування! 👌")

@bot.message_handler(commands=['check'])
def check_today(message):
    # Команда, щоб вручну перевірити, чи є сьогодні свято
    today = datetime.now().strftime("%d-%m")
    if today in birthdays:
        bot.reply_to(message, f"Так! Сьогодні святкує: {birthdays[today]} 🎂")
    else:
        bot.reply_to(message, "Сьогодні без тортів. Днів народження немає. zzz")

# --- ФУНКЦІЯ РОЗСИЛКИ ---
def send_birthday_message():
    today = datetime.now().strftime("%d-%m")
    
    if today in birthdays:
        name = birthdays[today]
        text = (
            f"🔔 **НАГАДУВАННЯ** 🔔\n\n"
            f"Сьогодні День народження святкує: **{name}**! 🎂\n"
            f"Не забудь привітати!"
        )
        
        users = get_subscribers()
        if not users:
            print("Немає підписників для розсилки.")
            return
        
        for user_id in users:
            try:
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
    
    # Плануємо час розсилки (можна змінити на свій)
    schedule.every().day.at("09:00").do(send_birthday_message)
    
    # Запускаємо планувальник в окремому потоці
    threading.Thread(target=schedule_checker, daemon=True).start()
    
    print("Бот запущений! Натисни /start у боті, щоб підписатися.")
    print("Keep-alive сервер працює на порту 8080")
    # Запускаємо самого бота (щоб він відповідав на повідомлення)
    bot.infinity_polling()
