import os
import telebot
import time
import logging
from datetime import datetime
from threading import Thread
from flask import Flask, request

# ==================== НАСТРОЙКИ ====================
# Берем из переменных окружения (безопаснее)
TOKEN = os.getenv("BOT_TOKEN", "8450359350:AAGWBUTpHyjH_piewfg4RnATqT8coacyzhw")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8488537910"))

# Создаем Flask приложение для вебхука
app = Flask(__name__)

# Инициализация бота
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== ВЕБСЕРВЕР ДЛЯ RENDER ====================

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kurush Digital Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 {
                color: #ff9f43;
            }
            .status {
                background: rgba(0, 255, 0, 0.2);
                padding: 10px;
                border-radius: 5px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Kurush Digital Telegram Bot</h1>
            <div class="status">
                ✅ Бот работает нормально
            </div>
            <p><strong>Администратор:</strong> Kurush Digital</p>
            <p><strong>Назначение:</strong> Поддержка приложения Isfara FM Radio</p>
            <p><strong>Bot:</strong> @KurushD_bot</p>
            <p><strong>Размещено на:</strong> Render.com</p>
            <p><strong>Время:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint для вебхука Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK'
    return 'Error'

# ==================== КОМАНДЫ БОТА ====================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
<b>👋 Добро пожаловать в Kurush Digital!</b>

Я - бот для поддержки приложения Isfara FM Radio.

<b>📞 Техподдержка:</b>
Просто напишите ваше сообщение ниже ⬇️

<b>⚡ Команды:</b>
/start - это меню
/support - помощь
/radio - о приложении
/status - статус бота

<b>Разработано:</b> Kurush Digital
    """
    bot.reply_to(message, welcome_text)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

@bot.message_handler(commands=['status'])
def bot_status(message):
    status_text = f"""
<b>🤖 Статус бота Kurush Digital</b>

✅ <b>Работает нормально</b>
📅 <b>Дата:</b> {datetime.now().strftime("%Y-%m-%d")}
⏰ <b>Время:</b> {datetime.now().strftime("%H:%M:%S")}
📍 <b>Хостинг:</b> Render.com
👑 <b>Админ:</b> Kurush Digital

<i>Бот для поддержки Isfara FM Radio</i>
    """
    bot.reply_to(message, status_text)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех сообщений"""
    
    user_info = f"""
<b>📨 НОВОЕ СООБЩЕНИЕ</b>

👤 <b>От:</b> {message.from_user.first_name or ''} {message.from_user.last_name or ''}
🆔 <b>ID:</b> <code>{message.from_user.id}</code>
📛 <b>Username:</b> @{message.from_user.username or 'нет'}

<b>📝 Текст:</b>
{message.text or '[без текста]'}

<b>⏰ Время:</b> {datetime.now().strftime("%H:%M:%S")}
    """
    
    try:
        # Отправляем вам
        bot.send_message(ADMIN_ID, user_info)
        
        # Пересылаем оригинал
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        # Подтверждение пользователю
        bot.reply_to(message, "✅ Сообщение получено! Я передал его Kurush Digital.")
        
        logger.info(f"Сообщение от {message.from_user.id} переслано")
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.reply_to(message, "⚠️ Ошибка отправки. Попробуйте позже.")

# ==================== ЗАПУСК ====================

def run_bot():
    """Запуск бота в отдельном потоке"""
    logger.info("Запуск бота в режиме polling...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Бот остановлен: {e}")

def run_web():
    """Запуск Flask сервера"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    print("="*50)
    print("🤖 Запуск Kurush Digital Bot на Render.com")
    print(f"👑 Админ: {ADMIN_ID}")
    print("="*50)
    
    # Запускаем в двух потоках
    bot_thread = Thread(target=run_bot, daemon=True)
    web_thread = Thread(target=run_web, daemon=True)
    
    bot_thread.start()
    web_thread.start()
    
    # Держим основной поток активным
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Остановка бота...")
