from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.db.models import Category, Product


def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for cat in categories:
        pair.append(InlineKeyboardButton(text=cat.title, callback_data=f"cat:{cat.id}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def products_kb(category_id: int, products: list[Product]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for p in products:
        area = f", {int(p.area_m2)} м²" if p.area_m2 else ""
        rows.append(
            [InlineKeyboardButton(text=f"{p.title}{area}", callback_data=f"prod:{p.id}")]
        )
    rows.append([InlineKeyboardButton(text="« К категориям", callback_data="catalog")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_card_kb(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉ Заказать этот проект", callback_data=f"lead_start:{product_id}")],
            [InlineKeyboardButton(text="« К списку моделей", callback_data=f"cat:{category_id}")],
            [InlineKeyboardButton(text="« К категориям", callback_data="catalog")],
        ]
    )
