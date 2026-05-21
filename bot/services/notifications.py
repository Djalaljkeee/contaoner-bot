from typing import Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.db.models import Lead


def lead_summary_text(lead: Lead, product_title: Optional[str] = None) -> str:
    lines = [
        f"🆕 <b>Заявка #{lead.id}</b>",
        f"<b>От:</b> {lead.name}, <code>{lead.phone}</code>",
        f"<b>Проект:</b> {product_title or 'общая'}",
        f"<b>Источник:</b> {lead.source.value}",
        f"<b>Сообщение:</b> {lead.message or '—'}",
    ]
    return "\n".join(lines)


def take_lead_kb(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Взять в работу", callback_data=f"lead_take:{lead_id}")]
        ]
    )


async def notify_managers(
    bot: Bot,
    chat_id: int,
    lead: Lead,
    product_title: Optional[str] = None,
) -> int:
    """Отправляет уведомление в чат менеджеров. Возвращает message_id."""
    msg = await bot.send_message(
        chat_id=chat_id,
        text=lead_summary_text(lead, product_title),
        reply_markup=take_lead_kb(lead.id),
        parse_mode="HTML",
    )
    return msg.message_id
