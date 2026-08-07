from aiogram.fsm.state import State, StatesGroup


class LateRequest(StatesGroup):
    choosing_tournament = State()
    waiting_nickname = State()
