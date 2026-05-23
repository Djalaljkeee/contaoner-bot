from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.db.models import CalcOption, DeliveryCity
from bot.services.calculator import fmt


def _price_label(delta: int) -> str:
    if delta == 0:
        return "включено"
    return f"+{fmt(delta)} ₽"


def module_kb(options: list[CalcOption]) -> InlineKeyboardMarkup:
    rows = []
    for opt in options:
        area = f" · {int(opt.area_m2)} м²" if opt.area_m2 else ""
        label = f"{opt.title}{area} — {fmt(int(opt.price_delta))} ₽"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"calc:mod:{opt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def insulation_kb(options: list[CalcOption]) -> InlineKeyboardMarkup:
    rows = []
    for opt in options:
        label = f"{opt.title} — {_price_label(int(opt.price_delta))}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"calc:ins:{opt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def foundation_kb(options: list[CalcOption]) -> InlineKeyboardMarkup:
    rows = []
    for opt in options:
        label = f"{opt.title} — +{fmt(int(opt.price_delta))} ₽"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"calc:fnd:{opt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def interior_kb(options: list[CalcOption]) -> InlineKeyboardMarkup:
    rows = []
    for opt in options:
        label = f"{opt.title} — {_price_label(int(opt.price_delta))}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"calc:int:{opt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def windows_kb(options: list[CalcOption]) -> InlineKeyboardMarkup:
    rows = []
    for opt in options:
        if int(opt.price_delta) == 0:
            label = opt.title
        else:
            label = f"{opt.title} — +{fmt(int(opt.price_delta))} ₽"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"calc:win:{opt.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def delivery_kb(cities: list[DeliveryCity]) -> InlineKeyboardMarkup:
    rows = []
    for city in cities:
        if city.distance_km == 0:
            label = f"🏭 {city.name}"
        else:
            cost = city.distance_km * 55
            label = f"{city.name} ({city.distance_km} км · {fmt(cost)} ₽)"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"calc:cit:{city.id}")])
    rows.append(
        [InlineKeyboardButton(text="📏 Ввести расстояние вручную", callback_data="calc:km")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def result_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Получить точный расчёт", callback_data="calc:lead"
                )
            ],
            [InlineKeyboardButton(text="🔄 Пересчитать", callback_data="calc:restart")],
        ]
    )
