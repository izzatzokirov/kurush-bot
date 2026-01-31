import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8483499301:AAG5278KznSFJnOIRcA-xnDps4GTxaD2uOI"
ADMIN_ID = 8488537910 

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    radio_issue = State()
    radio_model = State()
    radio_photo = State()
    service_type = State()
    client_name = State()
    client_phone = State()

# --- КРАСИВЫЕ КЛАВИАТУРЫ ---
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📻 Техподдержка Радио", callback_data="radio_hub"))
    builder.row(types.InlineKeyboardButton(text="💎 Заказать услуги Digital", callback_data="service_hub"))
    return builder.as_markup()

def radio_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔇 Нет звука", callback_data="err_no_sound"))
    builder.row(types.InlineKeyboardButton(text="📱 Приложение вылетает", callback_data="err_crash"))
    builder.row(types.InlineKeyboardButton(text="✍️ Другая проблема", callback_data="err_other"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main"))
    return builder.as_markup()

def service_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🌐 Создание сайта", callback_data="ser_site"))
    builder.row(types.InlineKeyboardButton(text="🎨 Логотип / Брендинг", callback_data="ser_logo"))
    builder.row(types.InlineKeyboardButton(text="🤖 Telegram бот", callback_data="ser_bot"))
    builder.row(types.InlineKeyboardButton(text="📞 Заказать звонок", callback_data="ser_call"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main"))
    return builder.as_markup()

# --- ОБРАБОТКА КОМАНД ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="📖 Что умеет бот?", callback_data="about_bot"))
    
    await message.answer(
        f"👋 Приветствую, {message.from_user.first_name}!\n\n"
        "Вы попали в **Kurush Digital**. Мы создаем цифровые решения и поддерживаем лучшие проекты страны.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "about_bot")
async def about_bot(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🚀 Начать работу", callback_data="back_main"))
    
    await callback.message.edit_text(
        "✨ **Возможности Kurush Bot:**\n\n"
        "✅ Помощь слушателям Isfara FM\n"
        "✅ Прием заявок на разработку сайтов\n"
        "✅ Быстрая связь с разработчиком\n"
        "✅ Отправка скриншотов ошибок",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Выберите нужный раздел:", reply_markup=main_menu())

# --- ВЕТКА РАДИО ---
@dp.callback_query(F.data == "radio_hub")
async def radio_hub(callback: types.CallbackQuery):
    await callback.message.edit_text("Что именно случилось? Выберите вариант или опишите сами:", reply_markup=radio_menu())

@dp.callback_query(F.data.startswith("err_"))
async def process_radio_error(callback: types.CallbackQuery, state: FSMContext):
    issue = callback.data
    await state.update_data(radio_issue=issue)
    await state.set_state(Form.radio_model)
    await callback.message.edit_text("Пожалуйста, напишите модель вашего телефона (например, Samsung A52 или iPhone 13):")

@dp.message(Form.radio_model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(radio_model=message.text)
    await state.set_state(Form.radio_photo)
    await message.answer("Почти готово! Пришлите скриншот ошибки (как фото):")

@dp.message(Form.radio_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    await bot.send_photo(ADMIN_ID, photo_id, caption=f"🆘 **ОШИБКА РАДИО**\nОт: @{message.from_user.username}\nТип: {data['radio_issue']}\nМодель: {data['radio_model']}")
    await message.answer("✅ Сообщение отправлено! Мы разберемся.", reply_markup=main_menu())
    await state.clear()

# --- ВЕТКА УСЛУГ ---
@dp.callback_query(F.data == "service_hub")
async def service_hub(callback: types.CallbackQuery):
    await callback.message.edit_text("Какие услуги вас интересуют?", reply_markup=service_menu())

@dp.callback_query(F.data == "ser_call")
async def service_call(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.client_name)
    await callback.message.edit_text("Введите ваше имя:")

@dp.message(Form.client_name)
async def process_client_name(message: types.Message, state: FSMContext):
    await state.update_data(client_name=message.text)
    await state.set_state(Form.client_phone)
    await message.answer("Введите ваш номер телефона для связи:")

@dp.message(Form.client_phone)
async def process_client_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_message(ADMIN_ID, f"💼 **НОВЫЙ ЗАКАЗ**\nИмя: {data['client_name']}\nТел: {message.text}\nОт: @{message.from_user.username}")
    await message.answer("📲 Спасибо! Мы свяжемся с вами в ближайшее время.", reply_markup=main_menu())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
