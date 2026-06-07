import logging

from maxapi import Router
from maxapi.types.updates.message_callback import MessageCallback
from maxapi.types.updates.message_created import MessageCreated
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.keyboards.catalog import product_nav_kb
from bot_max.keyboards.main import CATALOG_BTN
from bot_max.services.catalog import get_product, list_products

log = logging.getLogger(__name__)
router = Router()


def _product_caption(product) -> str:
    badge_map = {"hit": "🔥 Хит", "new": "🆕 Новинка", "premium": "⭐ Премиум"}
    lines = [f"{product.title}"]
    if product.badge:
        lines.append(badge_map.get(product.badge, ""))
    lines.append(f"Размер: {product.size_ft}")
    price_str = f"{product.price_from:,}".replace(",", " ")
    lines.append(f"Цена от: {price_str} ₽")
    if product.description:
        lines.append("")
        lines.append(product.description)
    return "\n".join(lines)


async def _show_page(target, session: AsyncSession, page: int) -> None:
    products = await list_products(session)
    if not products:
        await target.answer(text="Каталог пока пуст. Загляните позже!")
        return
    total = len(products)
    page = max(0, min(page, total - 1))
    product = products[page]
    caption = _product_caption(product)
    kb = product_nav_kb(page, total, product.id)
    await target.answer(text=caption, attachments=[kb])


@router.message_created.register
async def show_catalog(event: MessageCreated, session: AsyncSession):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != CATALOG_BTN:
        return
    await _show_page(event.message, session, 0)


@router.message_callback.register
async def catalog_page(event: MessageCallback, session: AsyncSession):
    payload = event.callback.payload or ""
    if not payload.startswith("maxcat:page:"):
        return
    try:
        page = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return
    products = await list_products(session)
    if not products:
        await event.ack(notification="Каталог пуст")
        return
    total = len(products)
    page = max(0, min(page, total - 1))
    product = products[page]
    caption = _product_caption(product)
    kb = product_nav_kb(page, total, product.id)
    await event.edit(text=caption, attachments=[kb])
    await event.ack()
