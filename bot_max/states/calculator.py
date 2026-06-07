from maxapi.context.state_machine import State, StatesGroup


class MaxCalcForm(StatesGroup):
    choosing_size = State()
    choosing_insulation = State()
    choosing_finishing = State()
    choosing_extras = State()
    showing_result = State()
