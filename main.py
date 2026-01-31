import asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web

TOKEN = "8483499301:AAG5278KznSFJnOIRcA-xnDps4GTxaD2uOI"
ADMIN = 8488537910
bot, dp = Bot(TOKEN), Dispatcher()

class Form(StatesGroup): r_issue = State(); r_model = State(); r_photo = State(); s_name = State(); s_phone = State()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def h(r): return web.Response(text="OK")
async def ws():
    a = web.Application(); a.router.add_get("/", h)
    runner = web.AppRunner(a); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()

# --- КНОПКИ ---
def kb(btns):
    b = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text=t, callback_data=c)] for t, c in btns])
    return b

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def st(m: types.Message):
    await m.answer(f"👋 Привет, {m.from_user.first_name}!\nЯ бот **Kurush Digital**.", reply_markup=kb([("📖 Что умею?", "about")]))

@dp.callback_query(F.data == "about")
async def ab(c: types.CallbackQuery):
    await c.message.edit_text("🚀 **Я помогаю:**\n1. Сообщить об ошибке радио.\n2. Заказать сайт/бота.", reply_markup=kb([("🎯 Начать", "main")]))

@dp.callback_query(F.data == "main")
async def mn(c: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("Выберите раздел:", reply_markup=kb([("📻 Радио", "r_hub"), ("💻 Услуги", "s_hub")]))

# Ветка Радио
@dp.callback_query(F.data == "r_hub")
async def rh(c: types.CallbackQuery):
    await c.message.edit_text("Что случилось?", reply_markup=kb([("🔇 Нет звука", "e1"), ("📱 Вылетает", "e2"), ("❓ Другое", "e3")]))

@dp.callback_query(F.data.startswith("e"))
async def re(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.r_model); await c.message.edit_text("Ваша модель телефона?")

@dp.message(Form.r_model)
async def rm(m: types.Message, state: FSMContext):
    await state.set_state(Form.r_photo); await m.answer("Пришлите скриншот ошибки:")

@dp.message(Form.r_photo, F.photo)
async def rp(m: types.Message, state: FSMContext):
    await bot.send_photo(ADMIN, m.photo[-1].file_id, caption=f"🆘 Радио: @{m.from_user.username}\nМодель: {m.text}")
    await m.answer("✅ Отправлено!", reply_markup=kb([("⬅️ Меню", "main")]))
    await state.clear()

# Ветка Услуг
@dp.callback_query(F.data == "s_hub")
async def sh(c: types.CallbackQuery):
    await c.message.edit_text("Что создадим?", reply_markup=kb([("🌐 Сайт", "s1"), ("🎨 Лого", "s2"), ("📞 Заказать звонок", "s_call")]))

@dp.callback_query(F.data == "s_call")
async def sc(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.s_name); await c.message.edit_text("Ваше имя?")

@dp.message(Form.s_name)
async def sn(m: types.Message, state: FSMContext):
    await state.set_state(Form.s_phone); await m.answer("Ваш номер телефона?")

@dp.message(Form.s_phone)
async def sp(m: types.Message, state: FSMContext):
    await bot.send_message(ADMIN, f"💼 Заказ: @{m.from_user.username}\nИмя: {m.text}")
    await m.answer("✅ Ждите звонка!", reply_markup=kb([("⬅️ Меню", "main")]))
    await state.clear()

async def start():
    asyncio.create_task(ws())
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(start())
