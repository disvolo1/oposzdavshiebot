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


bot = Bot(
    token=BOT_TOKEN
)


dp = Dispatcher(
    storage=MemoryStorage()
)


# Состояния

class LateForm(StatesGroup):
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
async def late_handler(callback: types.CallbackQuery):

    tournaments = today_tournaments()


    if not tournaments:

        await callback.message.answer(
            "Сегодня турниров не найдено 🙁"
        )

        return


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


    callback.message.bot.tournaments = tournaments


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


    tournaments = callback.message.bot.tournaments

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

@dp.message(LateForm.waiting_nickname)
async def nickname_handler(
    message: types.Message,
    state: FSMContext
):

    data = await state.get_data()

    tournament = data["tournament"]


    nickname = message.text


    await bot.send_message(
        ADMIN_ID,
        "🚨 Опоздание\n\n"
        f"🏓 {tournament['time']} — {tournament['title']}\n\n"
        f"👤 {nickname}"
    )


    await message.answer(
        "✅ Готово!\n\n"
        "Организатор получил информацию 🙌"
    )


    await state.clear()



# Запуск

async def main():

    print("🤖 PinkTablet Late Bot started")

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
