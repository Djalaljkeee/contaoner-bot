import logging
from typing import Any, Optional

from maxapi import Bot
from maxapi.types.attachments import AttachmentButton, CallbackButton, ButtonsPayload

from bot_max.db.models import MaxLead
from bot_max.services.calculator import fmt

log = logging.getLogger(__name__)


def _lead_text(lead: MaxLead) -> str:
    lines = [
        f"🆕 Новая заявка #{lead.id} — Петрикс-Хоум",
        f"Имя: {lead.name}",
        f"Телефон: {lead.phone}",
    ]
    if lead.product_title:
        lines.append(f"Проект: {lead.product_title}")
    if lead.message:
        lines.append(f"Сообщение: {lead.message}")
    if lead.calc_config:
        cfg = lead.calc_config
        lines.append("Конфигурация калькулятора:")
        if isinstance(cfg, dict):
            if "size" in cfg:
                lines.append(f"  Размер: {cfg['size'].get('title', '—')} — {fmt(cfg['size'].get('base_price', 0))} ₽")
            if "insulation" in cfg:
                lines.append(f"  Утепление: {cfg['insulation'].get('title', '—')}")
            if "finishing" in cfg:
                lines.append(f"  Отделка: {cfg['finishing'].get('title', '—')}")
            if cfg.get("extras_titles"):
                lines.append(f"  Доп: {', '.join(cfg['extras_titles'])}")
            if "total" in cfg:
                lines.append(f"  Итого: {fmt(cfg['total'])} ₽")
    return "\n".join(lines)


def _take_kb(lead_id: int) -> AttachmentButton:
    btn = CallbackButton(text="Взять в работу", payload=f"maxlead:take:{lead_id}")
    return AttachmentButton(
        type="inline_keyboard",
        payload=ButtonsPayload(buttons=[[btn]]),
    )


async def notify_manager(
    bot: Bot,
    manager_id: int,
    lead: MaxLead,
) -> None:
    try:
        await bot.send_message(
            user_id=manager_id,
            text=_lead_text(lead),
            attachments=[_take_kb(lead.id)],
        )
    except Exception:
        log.exception("Failed to notify manager %s about lead %s", manager_id, lead.id)
