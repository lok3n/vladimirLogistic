from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    input_name = State()
    input_number = State()


class ChangeStatus(StatesGroup):
    send_location_start = State()
    input_points = State()
    input_time_to_base = State()
    send_location_cancel = State()
