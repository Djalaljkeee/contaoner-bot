from typing import Any, Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.db.models import Lead, LeadType
from bot.services.calculator import fmt


def _calc_breakdown(cfg: dict) -> str:
    lines = [
        "  📦 Модуль: {title} — {price} ₽".format(
            title=cfg["module"]["title"], price=fmt(cfg["module"]["price"])
        ),
        "  🌡 Утепление: {title}{delta}".format(
            title=cfg["insulation"]["title"],
            delta=f" (+{fmt(cfg['insulation']['price_delta'])} ₽)" if cfg["insulation"]["price_delta"] else " (включено)",
        ),
        "  🏗 Фундамент: {title} (+{price} ₽)".format(
            title=cfg["foundation"]["title"], price=fmt(cfg["foundation"]["price_delta"])
        ),
        "  🛋 Интерьер: {title}{delta}".format(
            title=cfg["interior"]["title"],
            delta=f" (+{fmt(cfg['interior']['price_delta'])} ₽)" if cfg["interior"]["price_delta"] else " (включено)",
        ),
        "  🪟 Окна: {title}{delta}".format(
            title=cfg["windows"]["title"],
            delta=f" (+{fmt(cfg['windows']['price_delta'])} ₽)" if cfg["windows"]["price_delta"] else "",
        ),
    ]
    d = cfg["delivery"]
    if d["km"]:
        lines.append(f"  🚚 Доставка: {d['city']} ({d['km']} км) — {fmt(d['cost'])} ₽")
    else:
        lines.append(f"  🚚 Доставка: самовывоз")
    lines.append(f"  💰 ИТОГО: {fmt(cfg['total'])} ₽")
    return "\n".join(lines)


def lead_summary_text(
    lead: Lead,
    product_title: Optional[str] = None,
    calc_config: Optional[Any] = None,
) -> str:
    type_label = {
        LeadType.regular: "обычная",
        LeadType.calculator: "из калькулятора",
        LeadType.preorder: "предзаказ",
    }.get(lead.type, lead.type.value)

    lines = [
        f"🆕 <b>Заявка #{lead.id}</b> ({type_label})",
        f"<b>Имя:</b> {lead.name}",
        f"<b>Телефон:</b> <code>{lead.phone}</code>",
        f"<b>Источник:</b> {lead.source.value}",
    ]
    if product_title:
        lines.append(f"<b>Проект:</b> {product_title}")
    if lead.message:
        lines.append(f"<b>Сообщение:</b> {lead.message}")

    if calc_config:
        lines.append("<b>Конфигурация калькулятора:</b>")
        lines.append(_calc_breakdown(calc_config))

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
    calc_config: Optional[Any] = None,
) -> int:
    msg = await bot.send_message(
        chat_id=chat_id,
        text=lead_summary_text(lead, product_title, calc_config),
        reply_markup=take_lead_kb(lead.id),
        parse_mode="HTML",
    )
    return msg.message_id
