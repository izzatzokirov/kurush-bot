import asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = "8483499301:AAG5278KznSFJnOIRcA-xnDps4GTxaD2uOI"
ADMIN = 8488537910
bot, dp = Bot(TOKEN), Dispatcher()

class Form(StatesGroup):
    r_issue = State(); r_model = State(); r_photo = State()
    s_type = State(); s_name = State(); s_phone = State()

# --- СЕРВЕР ДЛЯ RENDER (ИСПРАВЛЕННЫЙ) ---
async def h(r): return web.Response(text="Kurush Digital Bot is Active")

async def start_ws():
    app = web.Application()
    app.router.add_get("/", h)
    runner = web.AppRunner(app)
    await runner.setup() # Исправляет ошибку RuntimeError
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

# --- КНОПКИ ---
def quick_kb(items, back=None):
    b = InlineKeyboardBuilder()
    for text, data in items: b.row(types.InlineKeyboardButton(text=text, callback_data=data))
    if back: b.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=back))
    return b.as_markup()

# --- ЛОГИКА (ГЛАВНОЕ МЕНЮ) ---
@dp.message(Command("start"))
async def start(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer(
        f"🚀 **Kurush Digital**\n\nПривет, {m.from_user.first_name}!\nЯ помогу вам с поддержкой радио или заказом IT-услуг.\n\nВыберите раздел: 👇",
        reply_markup=quick_kb([
            ("📻 Поддержка Isfara FM", "go_radio"),
            ("💎 Заказать IT-услуги", "go_services"),
            ("ℹ️ О компании", "go_about")
        ]), parse_mode="Markdown")

# (Сюда вставь все функции callback_query и message из прошлого кода)
# ... они остаются без изменений ...
@dp.callback_query(F.data == "home")
async def home(c: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("Выберите раздел:", 
        reply_markup=quick_kb([
            ("📻 Поддержка Isfara FM", "go_radio"),
            ("💎 Заказать IT-услуги", "go_services"),
            ("ℹ️ О компании", "go_about")
        ]))
# ... (и остальные функции обработки) ...

# --- ЗАПУСК ---
async def main():
    logging.info("Starting web server...")
    await start_ws()
    
    logging.info("Cleaning updates and starting bot...")
    # Удаляем вебхук и старые сообщения, чтобы не было ConflictError
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
