from aiogram.fsm.state import State, StatesGroup


class AdminServiceFSM(StatesGroup):
    waiting_new_price = State()


class AdminAddServiceFSM(StatesGroup):
    waiting_category = State()
    waiting_name = State()
    waiting_duration = State()
    waiting_price = State()


class AdminBlockSlotFSM(StatesGroup):
    waiting_range = State()


class AdminRejectFSM(StatesGroup):
    waiting_custom_reason = State()


class AdminDiscountFSM(StatesGroup):
    waiting_discount = State()
