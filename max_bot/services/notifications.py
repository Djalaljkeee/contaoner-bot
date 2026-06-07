import logging

from maxapi import Bot

from max_bot.config import settings
from max_bot.db.models import Lead

logger = logging.getLogger(__name__)


async def notify_manager(bot: Bot, lead: Lead) -> None:
    if not settings.manager_chat_id:
        return

    import json
    calc_text = ""
    if lead.calc_config:
        try:
            cfg = json.loads(lead.calc_config)
            calc_text = (
                f"\n📐 Конфигурация:\n"
                f"  Размер: {cfg.get('size', '—')}\n"
                f"  Утепление: {cfg.get('insulation', '—')}\n"
                f"  Отделка: {cfg.get('finish', '—')}\n"
                f"  Опции: {', '.join(cfg.get('options', [])) or 'нет'}\n"
                f"  Итого: {cfg.get('total', 0):,} ₽".replace(",", " ")
            )
        except Exception:
            pass

    text = (
        f"📩 Новая заявка #{lead.id}\n\n"
        f"👤 Имя: {lead.name}\n"
        f"📞 Телефон: {lead.phone}\n"
        f"📌 Источник: {lead.source}"
        f"{calc_text}"
    )

    try:
        await bot.send_message(chat_id=settings.manager_chat_id, text=text)
    except Exception as e:
        logger.warning("Не удалось отправить уведомление менеджеру: %s", e)
