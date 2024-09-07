from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    input_name = State()
    input_number = State()


class ChangeStatus(StatesGroup):
    input_points = State()
    input_time_to_base = State()
