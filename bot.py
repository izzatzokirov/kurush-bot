import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

# Данные
TOKEN = "8483499301:AAG5278KznSFJnOIRcA-xnDps4GTxaD2uOI"
ADMIN_ID = 8488537910 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояния для анкет
class SupportStates(StatesGroup):
    desc = State()
    model = State()
    screenshot = State()

class OrderStates(StatesGroup):
    name = State()
    phone = State()
    question = State()

# --- КНОПКИ ---
def get_main_kb():
    kb = [
        [types.KeyboardButton(text="🛠 Поддержка Радио")],
        [types.KeyboardButton(text="💻 Заказать услуги (Сайт/Бот)")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот Kurush Digital.\n"
        "Выберите, что вас интересует:", 
        reply_markup=get_main_kb()
    )

# --- ЛОГИКА ПОДДЕРЖКИ РАДИО ---
@dp.message(F.text == "🛠 Поддержка Радио")
async def support_start(message: types.Message, state: FSMContext):
    await state.set_state(SupportStates.desc)
    await message.answer("Опишите вашу проблему:")

@dp.message(SupportStates.desc)
async def support_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await state.set_state(SupportStates.model)
    await message.answer("Какая у вас модель телефона?")

@dp.message(SupportStates.model)
async def support_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(SupportStates.screenshot)
    await message.answer("Отправьте скриншот проблемы (как фото):")

@dp.message(SupportStates.screenshot, F.photo)
async def support_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    
    # Отправка тебе (админу)
    await bot.send_photo(
        ADMIN_ID, photo_id,
        caption=f"🆘 **ПРОБЛЕМА С РАДИО**\nОт: @{message.from_user.username}\n"
                f"Описание: {data['desc']}\nМодель: {data['model']}"
    )
    await message.answer("Спасибо! Данные переданы разработчику. Мы скоро свяжемся с вами.", reply_markup=get_main_kb())
    await state.clear()

# --- ЛОГИКА ЗАКАЗА УСЛУГ ---
@dp.message(F.text == "💻 Заказать услуги (Сайт/Бот)")
async def order_start(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.name)
    await message.answer("Как вас зовут?")

@dp.message(OrderStates.name)
async def order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.phone)
    await message.answer("Ваш номер телефона?")

@dp.message(OrderStates.phone)
async def order_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.question)
    await message.answer("Какой у вас вопрос или какой проект хотите заказать?")

@dp.message(OrderStates.question)
async def order_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    # Отправка тебе (админу)
    await bot.send_message(
        ADMIN_ID,
        f"💼 **НОВЫЙ ЗАКАЗ УСЛУГ**\nОт: @{message.from_user.username}\n"
        f"Имя: {data['name']}\nТел: {data['phone']}\nВопрос: {message.text}"
    )
    await message.answer("Ваша заявка принята! Мы позвоним вам в ближайшее время.", reply_markup=get_main_kb())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
