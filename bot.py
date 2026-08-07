import asyncio
import os
import re

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    State,
    StatesGroup
)

from parser import today_tournaments

from database import (
    save_late_request,
    get_late_users,
    get_admin_message,
    save_admin_message
)


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()



# ==========================
# FSM
# ==========================

class LateState(StatesGroup):

    waiting_nickname = State()



# ==========================
# ЧИСТКА ТЕКСТА
# ==========================

def clean_text(text):

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )

    return " ".join(
        text.split()
    ).strip()



# ==========================
# START
# ==========================

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



# ==========================
# НАЖАЛИ ОПАЗДЫВАЮ
# ==========================

@dp.callback_query(
    lambda c: c.data == "late"
)
async def late_handler(
    callback: types.CallbackQuery
):

    await callback.answer()


    tournaments = today_tournaments()


    print(
        "ТУРНИРЫ ДЛЯ ВЫБОРА:",
        tournaments
    )


    if not tournaments:

        await callback.message.answer(
            "Сегодня турниров не найдено 🙁"
        )

        return



    buttons = []


    for index, tournament in enumerate(tournaments):

        text = (
            f"🕒 {tournament['time']} • "
            f"{tournament['title']}"
        )


        buttons.append(
            [
                InlineKeyboardButton(
                    text=text[:60],
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



# ==========================
# ВЫБРАЛ ТУРНИР
# ==========================

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


    tournament_name = clean_text(
        f"{tournament['time']} • {tournament['title']}"
    )


    print(
        "ВЫБРАН ТУРНИР:",
        tournament_name
    )


    await state.update_data(
        tournament=tournament_name
    )


    await state.set_state(
        LateState.waiting_nickname
    )


    print(
        "СОСТОЯНИЕ УСТАНОВЛЕНО"
    )


    await callback.message.answer(
        "Напишите свой ник 👇"
    )



# ==========================
# ПОЛУЧИЛ НИК
# ==========================

@dp.message(
    LateState.waiting_nickname
)
async def nickname_handler(
    message: types.Message,
    state: FSMContext
):

    print(
        "ПОЛУЧИЛ НИК:",
        message.text
    )


    data = await state.get_data()


    tournament = data.get(
        "tournament"
    )


    if not tournament:

        await message.answer(
            "Ошибка. Выберите турнир заново."
        )

        await state.clear()

        return



    username = clean_text(
        message.text
    )


    try:

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


        old_message_id = await get_admin_message(
            tournament
        )


        if old_message_id:


            try:

                await bot.edit_message_text(
                    chat_id=ADMIN_ID,
                    message_id=old_message_id,
                    text=admin_text
                )


                print(
                    "СООБЩЕНИЕ АДМИНА ОБНОВЛЕНО"
                )


            except Exception as e:

                print(
                    "ОШИБКА EDIT:",
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


            print(
                "НОВОЕ СООБЩЕНИЕ АДМИНУ:",
                msg.message_id
            )



        await message.answer(
            "✅ Спасибо!\n\n"
            "Организатор получил информацию 🙌"
        )


    except Exception as e:


        print(
            "ОШИБКА В NICK HANDLER:",
            e
        )


        await message.answer(
            "❌ Ошибка. Попробуйте ещё раз."
        )



    finally:

        await state.clear()



# ==========================
# RUN
# ==========================

async def main():

    print(
        "🤖 PinkTablet Late Bot started"
    )


    await dp.start_polling(
        bot
    )



if __name__ == "__main__":

    asyncio.run(main())
