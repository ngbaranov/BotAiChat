from aiogram.fsm.state import StatesGroup, State


# Состояния для FSM
class BotStates(StatesGroup):
    choosing_provider = State()
    choosing_model = State()
    ready = State()
