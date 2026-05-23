from aiogram.fsm.state import State, StatesGroup


class CalcForm(StatesGroup):
    choosing_module = State()
    choosing_insulation = State()
    choosing_foundation = State()
    choosing_interior = State()
    choosing_windows = State()
    choosing_delivery = State()
    entering_distance = State()
    showing_result = State()
