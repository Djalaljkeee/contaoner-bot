from maxapi.filters.state import State, StatesGroup


class CalcForm(StatesGroup):
    choosing_size = State()
    choosing_insulation = State()
    choosing_finish = State()
    choosing_options = State()
    showing_result = State()
