from maxapi.filters.state import State, StatesGroup


class LeadForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    confirming = State()
