import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from database import save_late_request


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")


bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()


# Стартовое сообщение

@dp.message(CommandStart())
async def start_handler(message: types.Message):

    await message.answer(
        "🏓 Привет!\n\n"
        "Это бот для опоздавших участников PinkTablet.\n\n"
        "Если ты опаздываешь на турнир — отправь сюда:\n\n"
        "• имя\n"
        "• название турнира\n"
        "• сколько минут опаздываешь\n\n"
        "Организатор получит информацию и постарается помочь 🙌"
    )


# Получение заявки

@dp.message()
async def late_request_handler(message: types.Message):

    user_id = message.from_user.id

    username = (
        message.from_user.username
        if message.from_user.username
        else "без_username"
    )


    if message.text:
        text = message.text

    elif message.photo:
        text = "Пользователь отправил фото"

    elif message.voice:
        text = "Пользователь отправил голосовое сообщение"

    elif message.video:
        text = "Пользователь отправил видео"

    else:
        text = "Пользователь отправил неизвестный тип сообщения"


    await save_late_request(
        user_id=user_id,
        username=username,
        text=text
    )


    await message.answer(
        "✅ Заявка получена!\n\n"
        "Мы передали информацию организатору турнира.\n"
        "Постараемся помочь 🙌"
    )


# Запуск бота

async def main():

    print("🤖 PinkTablet Late Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
