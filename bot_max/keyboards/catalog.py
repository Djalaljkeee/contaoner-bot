from maxapi.enums.attachment import AttachmentType
from maxapi.types.attachments import (
    AttachmentButton,
    ButtonsPayload,
    CallbackButton,
)

from bot_max.db.models import MaxProduct


def _badge_label(badge: str | None) -> str:
    mapping = {"hit": " 🔥 Хит", "new": " 🆕 Новинка", "premium": " ⭐ Премиум"}
    return mapping.get(badge or "", "") if badge else ""


def product_nav_kb(page: int, total: int, product_id: int) -> AttachmentButton:
    nav_row = []
    if page > 0:
        nav_row.append(CallbackButton(text="◀", payload=f"maxcat:page:{page - 1}"))
    nav_row.append(
        CallbackButton(text=f"{page + 1}/{total}", payload=f"maxcat:page:{page}")
    )
    if page < total - 1:
        nav_row.append(CallbackButton(text="▶", payload=f"maxcat:page:{page + 1}"))

    order_row = [
        CallbackButton(text="Заказать проект", payload=f"maxlead:prod:{product_id}")
    ]
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(buttons=[nav_row, order_row]),
    )
