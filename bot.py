import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from database import save_late_request


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


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


@dp.message()
async def late_request_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text

    await save_late_request(
        user_id=user_id,
        username=username,
        message=text
    )

    await message.answer(
        "✅ Информация отправлена организатору.\n"
        "Если что-то изменится — напиши ещё одним сообщением."
    )


async def main():
    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
