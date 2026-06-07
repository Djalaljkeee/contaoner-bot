from maxapi.context.state_machine import State, StatesGroup


class MaxLeadForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    confirming = State()
