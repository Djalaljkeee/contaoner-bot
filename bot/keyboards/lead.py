from typing import Optional

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

CANCEL_BTN = "✖ Отменить"
SKIP_BTN = "Пропустить"
SHARE_CONTACT_BTN = "📱 Поделиться контактом"


def use_name_kb(suggested: Optional[str]) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = []
    if suggested:
        rows.append([KeyboardButton(text=f"Использовать «{suggested}»")])
    rows.append([KeyboardButton(text=CANCEL_BTN)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def phone_kb(saved_phone: Optional[str] = None) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=SHARE_CONTACT_BTN, request_contact=True)]
    ]
    if saved_phone:
        rows.append([KeyboardButton(text=f"Использовать {saved_phone}")])
    rows.append([KeyboardButton(text=CANCEL_BTN)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def message_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SKIP_BTN)],
            [KeyboardButton(text=CANCEL_BTN)],
        ],
        resize_keyboard=True,
    )


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить", callback_data="lead_send")],
            [InlineKeyboardButton(text="✏ Изменить", callback_data="lead_edit")],
            [InlineKeyboardButton(text="✖ Отменить", callback_data="lead_cancel")],
        ]
    )
