from maxapi import Dispatcher, Router
from maxapi.context import BaseContext
from maxapi.filters import F
from maxapi.types import MessageCallback

from max_bot.keyboards.catalog import catalog_card_kb, catalog_list_kb
from max_bot.services.catalog import PROJECTS

router = Router()

_LIST_TEXT = "🏠 Выберите проект для просмотра:"


def _card_text(idx: int) -> str:
    p = PROJECTS[idx]
    return (
        f"📦 {p.title}\n"
        f"📐 Размер: {p.size}\n"
        f"💰 Цена от: {p.price:,} ₽\n\n"
        f"{p.description}"
    ).replace(",", " ")


@router.message_callback(F.callback.payload == "menu:catalog")
async def show_catalog_list(event: MessageCallback, context: BaseContext) -> None:
    await event.edit(_LIST_TEXT, attachments=[catalog_list_kb().pack()])


@router.message_callback(F.callback.payload.startswith("catalog:show:"))
async def show_project_card(event: MessageCallback) -> None:
    payload = event.callback.payload or ""
    try:
        idx = int(payload.split(":")[-1])
    except (ValueError, IndexError):
        idx = 0

    idx = max(0, min(idx, len(PROJECTS) - 1))
    await event.edit(_card_text(idx), attachments=[catalog_card_kb(idx).pack()])


def register(dp: Dispatcher) -> None:
    dp.include_routers(router)
