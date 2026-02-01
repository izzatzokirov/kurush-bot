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

# --- СЕРВЕР ДЛЯ RENDER ---
async def h(r): return web.Response(text="Kurush Digital Bot is Active")
async def ws():
    a = web.Application(); a.router.add_get("/", h)
    await web.TCPSite(web.AppRunner(a), "0.0.0.0", 10000).start()

# --- УМНЫЙ КОНСТРУКТОР КНОПОК ---
def quick_kb(items, back=None):
    b = InlineKeyboardBuilder()
    for text, data in items: b.row(types.InlineKeyboardButton(text=text, callback_data=data))
    if back: b.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=back))
    return b.as_markup()

# --- ГЛАВНОЕ МЕНЮ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        f"🚀 **Kurush Digital v2.0**\n\nПривет, {m.from_user.first_name}! Я твой проводник в мир цифровых решений.\n\n"
        "Выберите, чем я могу быть полезен сегодня: 👇",
        reply_markup=quick_kb([
            ("📻 Поддержка Isfara FM", "go_radio"),
            ("💎 Заказать IT-услуги", "go_services"),
            ("ℹ️ О компании", "go_about")
        ]), parse_mode="Markdown")

# --- ЛОГИКА "О НАС" ---
@dp.callback_query(F.data == "go_about")
async def about(c: types.CallbackQuery):
    await c.message.edit_text(
        "✨ **Kurush Digital** — это не просто код. Это развитие.\n\n"
        "• Разработка приложений (как Isfara FM)\n"
        "• Автоматизация бизнеса через ботов\n"
        "• Дизайн, который запоминают.\n\n"
        "Мы делаем сложные вещи простыми.",
        reply_markup=quick_kb([], back="home"))

# --- ВЕТКА РАДИО (ТЕХПОДДЕРЖКА) ---
@dp.callback_query(F.data == "go_radio")
async def radio_main(c: types.CallbackQuery):
    await c.message.edit_text("Что случилось с радио?", 
        reply_markup=quick_kb([
            ("🔇 Нет звука", "err_sound"),
            ("📵 Не открывается", "err_app"),
            ("💬 Другая проблема", "err_other")
        ], back="home"))

@dp.callback_query(F.data.startswith("err_"))
async def radio_step1(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(issue=c.data)
    await state.set_state(Form.r_model)
    await c.message.edit_text("📝 Понял. Какая у вас **модель телефона**?")

@dp.message(Form.r_model)
async def radio_step2(m: types.Message, state: FSMContext):
    await state.update_data(model=m.text)
    await state.set_state(Form.r_photo)
    await m.answer("📸 Почти готово! Пришлите **скриншот** ошибки:")

@dp.message(Form.r_photo, F.photo)
async def radio_final(m: types.Message, state: FSMContext):
    d = await state.get_data()
    await bot.send_photo(ADMIN, m.photo[-1].file_id, 
        caption=f"🆘 **ОШИБКА РАДИО**\nОт: @{m.from_user.username}\nСуть: {d['issue']}\nМодель: {d['model']}")
    await m.answer("✅ Отправлено! Разработчик уже изучает проблему.", reply_markup=quick_kb([("🏠 В начало", "home")]))
    await state.clear()

# --- ВЕТКА УСЛУГ (КВИЗ) ---
@dp.callback_query(F.data == "go_services")
async def serv_main(c: types.CallbackQuery):
    await c.message.edit_text("💎 **Что создадим для вас?**", 
        reply_markup=quick_kb([
            ("🌐 Современный Сайт", "type_site"),
            ("🤖 Telegram Бот", "type_bot"),
            ("🎨 Логотип / Брендинг", "type_logo"),
            ("📞 Заказать звонок", "type_call")
        ], back="home"))

@dp.callback_query(F.data.startswith("type_"))
async def serv_step1(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=c.data)
    await state.set_state(Form.s_name)
    await c.message.edit_text("🤝 Отличный выбор! Как к вам обращаться (Ваше имя)?")

@dp.message(Form.s_name)
async def serv_step2(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await state.set_state(Form.s_phone)
    await m.answer(f"Приятно познакомиться, {m.text}! Теперь введите ваш **номер телефона**:")

@dp.message(Form.s_phone)
async def serv_final(m: types.Message, state: FSMContext):
    d = await state.get_data()
    await bot.send_message(ADMIN, f"💼 **НОВЫЙ ЗАКАЗ**\nУслуга: {d['type']}\nИмя: {d['name']}\nТел: {m.text}\nОт: @{m.from_user.username}")
    await m.answer("🚀 Заявка принята! Мы свяжемся с вами в течение часа.", reply_markup=quick_kb([("🏠 В начало", "home")]))
    await state.clear()

# --- ОБРАБОТЧИК КНОПКИ НАЗАД ---
@dp.callback_query(F.data == "home")
async def home(c: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("Выберите раздел:", 
        reply_markup=quick_kb([
            ("📻 Поддержка Isfara FM", "go_radio"),
            ("💎 Заказать IT-услуги", "go_services"),
            ("ℹ️ О компании", "go_about")
        ]))

async def main():
    asyncio.create_task(ws())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
