import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_IDS
from database import save_late_request


bot = Bot(
    token=BOT_TOKEN,
    parse_mode=ParseMode.HTML
)


dp = Dispatcher()


START_TEXT = """
🏓 <b>PinkTablet</b>

Это бот для опоздавших игроков.

Если ты опаздываешь на турнир — напиши:

• сколько минут задерживаешься
• причину

Например:
<i>Буду через 10 минут, пробки</i>
"""


@dp.message(F.text == "/start")
async def start(message: Message):

    await message.answer(
        START_TEXT
    )


@dp.message()
async def late_request(message: Message):

    if message.from_user.is_bot:
        return


    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "нет username"
    )


    name = message.from_user.full_name


    text = (
        message.text
        if message.text
        else "медиа-сообщение"
    )


    try:

        save_late_request(
            telegram_id=message.from_user.id,
            username=username,
            name=name,
            message=text
        )


    except Exception as e:

        print(
            "Database error:",
            e
        )


    admin_text = f"""
🚨 <b>ОПОЗДАНИЕ</b>

👤 Игрок:
{name}

📱 Telegram:
{username}

🆔 ID:
{message.from_user.id}

💬 Сообщение:
{text}
"""


    for admin_id in ADMIN_IDS:

        try:

            await bot.send_message(
                admin_id,
                admin_text
            )

        except Exception as e:

            print(
                "Admin error:",
                e
            )


    await message.answer(
        "✅ Организатор получил уведомление.\n"
        "Ожидай решения 🏓"
    )



async def main():

    print(
        "PinkTablet late bot started"
    )


    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(main())
