import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from database import save_late_request


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()


# Стартовое сообщение
@dp.message(CommandStart())
async def start_handler(message: types.Message):

    await message.answer(
        "👋 Привет!\n\n"
        "Это бот для опоздавших участников.\n\n"
        "Если ты опоздал на турнир — напиши сюда:\n"
        "• имя\n"
        "• на какой турнир\n"
        "• сколько опаздываешь\n\n"
        "Мы передадим информацию организатору."
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

    text = message.text


    await save_late_request(
        user_id=user_id,
        username=username,
        text=text
    )


    await message.answer(
        "✅ Спасибо!\n\n"
        "Информация передана организатору."
    )


# Запуск
async def main():

    print("🤖 Bot started")

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(main())
