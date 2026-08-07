from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏓 Я опаздываю на турнир",
                    callback_data="late"
                )
            ]
        ]
    )


def arrived_keyboard(request_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Я пришел",
                    callback_data=f"arrived:{request_id}"
                )
            ]
        ]
    )


def tournaments_keyboard(tournaments):
    keyboard = []

    for i, t in enumerate(tournaments):
        keyboard.append([
            InlineKeyboardButton(
                text=f"{t['time']} • {t['title']}",
                callback_data=f"tour:{i}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
