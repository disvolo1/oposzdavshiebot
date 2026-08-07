import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from parser import today_tournaments

from database import (
    save_late_request,
    get_late_users,
    get_admin_message,
    save_admin_message
)


load_dotenv()


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


ADMIN_ID = int(
    os.getenv("ADMIN_ID")
)



bot = Bot(
    token=BOT_TOKEN
)


dp = Dispatcher()



# состояния

class LateState(StatesGroup):

    waiting_nickname = State()



# старт

@dp.message(CommandStart())
async def start_handler(
    message: types.Message
):

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
        "Если ты опаздываешь на турнир — нажми кнопку:",
        reply_markup=keyboard
    )



# нажали опаздываю

@dp.callback_query(
    lambda c: c.data == "late"
)
async def late_handler(
    callback: types.CallbackQuery
):

    await callback.answer()


    tournaments = today_tournaments()


    if not tournaments:


        await callback.message.answer(
            "Сегодня турниров не найдено 🙁"
        )

        return



    buttons = []


    for index, tournament in enumerate(tournaments):


        title = (
            f"🕒 {tournament['time']} • "
            f"{tournament['title']}"
        )


        buttons.append(
            [
                InlineKeyboardButton(
                    text=title[:60],
                    callback_data=f"tour_{index}"
                )
            ]
        )


    await callback.message.answer(
        "Выберите турнир:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )



# выбран турнир

@dp.callback_query(
    lambda c: c.data.startswith("tour_")
)
async def tournament_selected(
    callback: types.CallbackQuery,
    state: FSMContext
):

    await callback.answer()


    index = int(
        callback.data.split("_")[1]
    )


    tournaments = today_tournaments()


    tournament = tournaments[index]


    tournament_name = (
        f"{tournament['time']} • "
        f"{tournament['title']}"
    )


    await state.update_data(
        tournament=tournament_name
    )


    await state.set_state(
        LateState.waiting_nickname
    )


    await callback.message.answer(
        "Напишите свой ник 👇"
    )



# ник пользователя

@dp.message(
    LateState.waiting_nickname
)
async def nickname_handler(
    message: types.Message,
    state: FSMContext
):


    data = await state.get_data()


    tournament = data[
        "tournament"
    ]


    username = message.text.strip()



    await save_late_request(

        user_id=message.from_user.id,

        username=username,

        tournament=tournament

    )



    users = await get_late_users(
        tournament
    )


    admin_text = (
        f"🏓 Опоздание\n\n"
        f"{tournament}\n\n"
        f"Участники:\n\n"
    )


    for user in users:

        admin_text += (
            f"🟡 {user}\n"
        )



    old_message = await get_admin_message(
        tournament
    )



    if old_message:


        try:

            await bot.edit_message_text(

                chat_id=ADMIN_ID,

                message_id=old_message,

                text=admin_text

            )


        except Exception as e:

            print(
                "Ошибка обновления:",
                e
            )



    else:


        msg = await bot.send_message(

            chat_id=ADMIN_ID,

            text=admin_text

        )


        await save_admin_message(

            tournament,

            msg.message_id

        )



    await message.answer(
        "✅ Спасибо!\n\n"
        "Организатор получил информацию 🙌"
    )


    await state.clear()



# запуск

async def main():

    print(
        "🤖 PinkTablet Late Bot started"
    )


    await dp.start_polling(
        bot
    )



if __name__ == "__main__":

    asyncio.run(main())
