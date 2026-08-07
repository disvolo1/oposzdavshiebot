import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from parser import today_tournaments


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID не найден")


bot = Bot(
    token=BOT_TOKEN
)


dp = Dispatcher(
    storage=MemoryStorage()
)


# Состояния пользователя

class LateForm(StatesGroup):
    waiting_tournament = State()
    waiting_nickname = State()



# /start

@dp.message(CommandStart())
async def start_handler(message: types.Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏓 Я опаздываю",
                    callback_data="late"
                )
            ]
        ]
    )


    await message.answer(
        "🏓 Привет!\n\n"
        "Это бот для опоздавших участников PinkTablet.\n\n"
        "Если ты опаздываешь на турнир — нажми кнопку ниже 👇",
        reply_markup=keyboard
    )



# Кнопка "Я опаздываю"

@dp.callback_query(lambda c: c.data == "late")
async def late_handler(
    callback: types.CallbackQuery,
    state: FSMContext
):

    tournaments = today_tournaments()


    if not tournaments:

        await callback.message.answer(
            "Сегодня турниров не найдено 🙁"
        )

        await callback.answer()

        return


    await state.update_data(
        tournaments=tournaments
    )


    buttons = []


    for index, tournament in enumerate(tournaments):

        buttons.append(
            [
                InlineKeyboardButton(
                    text=(
                        f'🕒 {tournament["time"]} • '
                        f'{tournament["title"]}'
                    ),
                    callback_data=f"tournament_{index}"
                )
            ]
        )


    await callback.message.answer(
        "Выберите турнир:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await state.set_state(
        LateForm.waiting_tournament
    )


    await callback.answer()



# Выбор турнира

@dp.callback_query(
    lambda c: c.data.startswith("tournament_")
)
async def tournament_selected(
    callback: types.CallbackQuery,
    state: FSMContext
):

    index = int(
        callback.data.split("_")[1]
    )


    data = await state.get_data()

    tournaments = data.get(
        "tournaments",
        []
    )


    if index >= len(tournaments):

        await callback.message.answer(
            "Ошибка выбора турнира"
        )

        await callback.answer()

        return


    tournament = tournaments[index]


    await state.update_data(
        tournament=tournament
    )


    await state.set_state(
        LateForm.waiting_nickname
    )


    await callback.message.answer(
        "Напишите свой ник 👤"
    )


    await callback.answer()



# Получение ника

@dp.message(
    LateForm.waiting_nickname
)
async def nickname_handler(
    message: types.Message,
    state: FSMContext
):

    data = await state.get_data()

    tournament = data["tournament"]


    nickname = message.text


    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "без username"
    )


    await bot.send_message(
        ADMIN_ID,
        "🚨 Новый запрос на опоздание\n\n"
        f"🏓 Турнир:\n"
        f"{tournament['time']} — {tournament['title']}\n\n"
        f"👤 Ник:\n"
        f"{nickname}\n\n"
        f"Telegram:\n"
        f"{username}"
    )


    await message.answer(
        "✅ Готово!\n\n"
        "Организатор получил информацию 🙌"
    )


    await state.clear()



# Запуск

async def main():

    print(
        "🤖 PinkTablet Late Bot started"
    )

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
