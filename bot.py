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
# CLEAN TEXT
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


    msg = await message.answer(
        "🏓 Привет!\n\n"
        "Это бот для опаздывающих на турниры пингтаблет.\n\n"
        "Если ты опаздываешь на турнир — нажми кнопку:",
        reply_markup=keyboard
    )


    # закрепляем приветствие

    try:

        await bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            disable_notification=True
        )

        print(
            "ПРИВЕТСТВИЕ ЗАКРЕПЛЕНО"
        )

    except Exception as e:

        print(
            "ОШИБКА ЗАКРЕПЛЕНИЯ:",
            e
        )



# ==========================
# КНОПКА ОПОЗДАЮ
# ==========================

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

        title = clean_text(
            tournament["title"]
        )


        buttons.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"🕒 {tournament['time']} • {title}"
                    )[:60],
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
# ВЫБОР ТУРНИРА
# ==========================

@dp.callback_query(
    lambda c: c.data.startswith("tour_")
)
async def tournament_selected(
    callback: types.CallbackQuery,
    state: FSMContext
):

    await callback.answer()


    try:

        await callback.message.delete()

    except:

        pass



    index = int(
        callback.data.split("_")[1]
    )


    tournaments = today_tournaments()


    tournament = tournaments[index]


    tournament_name = clean_text(
        f"{tournament['time']} • {tournament['title']}"
    )


    await state.update_data(
        tournament=tournament_name
    )


    await state.set_state(
        LateState.waiting_nickname
    )


    msg = await callback.message.answer(
        "Напишите свой ник 👇"
    )


    await state.update_data(
        nickname_message_id=msg.message_id
    )



# ==========================
# НИК
# ==========================

@dp.message(
    LateState.waiting_nickname
)
async def nickname_handler(
    message: types.Message,
    state: FSMContext
):

    data = await state.get_data()


    try:

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=data.get(
                "nickname_message_id"
            )
        )

    except:

        pass



    try:

        await message.delete()

    except:

        pass



    nickname = clean_text(
        message.text
    )


    tournament = data.get(
        "tournament"
    )



    try:


        await save_late_request(
            user_id=message.from_user.id,
            username=nickname,
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
                f'<a href="tg://user?id={user["user_id"]}">'
                f'{user["username"]}'
                f'</a>\n'
            )



        old_message_id = await get_admin_message(
            tournament
        )



        if old_message_id:


            try:

                await bot.edit_message_text(
                    chat_id=ADMIN_ID,
                    message_id=old_message_id,
                    text=admin_text,
                    parse_mode="HTML"
                )


            except Exception as e:

                print(
                    "Ошибка обновления:",
                    e
                )



        else:


            msg = await bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                parse_mode="HTML"
            )


            await save_admin_message(
                tournament,
                msg.message_id
            )



        await message.answer(
            "✅ Спасибо!\n\n"
            "Организаторы получили информацию 🙌"
        )


        await state.clear()



    except Exception as e:


        print(
            "ОШИБКА:",
            e
        )


        await message.answer(
            "❌ Ошибка. Попробуйте ещё раз."
        )



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
