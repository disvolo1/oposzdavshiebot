import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [
    int(x)
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip()
]

bot = Bot(
    token=BOT_TOKEN,
    parse_mode=ParseMode.HTML
)

dp = Dispatcher()


START_TEXT = """
Привет! 👋

Это бот для опоздавших игроков PinkTablet.

Если ты опаздываешь на турнир — напиши сюда:

• имя и фамилию
• на сколько минут опаздываешь
• причину (по желанию)

Администратор получит сообщение и решит вопрос с твоим участием.
"""


@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(START_TEXT)


@dp.message()
async def handle_late_player(message: Message):

    if message.from_user.is_bot:
        return

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "без username"
    )

    text = f"""
🚨 <b>Игрок опаздывает</b>

👤 Игрок: {message.from_user.full_name}
🔗 Username: {username}
🆔 ID: {message.from_user.id}

Сообщение:
{message.text or "медиа-сообщение"}
"""

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                text
            )
        except Exception as e:
            print(
                f"Ошибка отправки админу {admin_id}: {e}"
            )

    await message.answer(
        "✅ Сообщение отправлено администратору.\n"
        "Ожидай решения по турниру."
    )


async def main():
    print("Late player bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
