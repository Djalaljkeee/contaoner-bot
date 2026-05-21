from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CATALOG_BTN = "📦 Каталог решений"
LEAD_BTN = "✉ Оставить заявку"
ABOUT_BTN = "ℹ О компании"
CONTACTS_BTN = "📞 Контакты"


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CATALOG_BTN)],
            [KeyboardButton(text=LEAD_BTN)],
            [KeyboardButton(text=ABOUT_BTN), KeyboardButton(text=CONTACTS_BTN)],
        ],
        resize_keyboard=True,
    )
