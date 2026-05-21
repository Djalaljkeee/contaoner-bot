from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Product
from bot.keyboards.catalog import categories_kb, product_card_kb, products_kb
from bot.keyboards.main import CATALOG_BTN
from bot.services.catalog import (
    cache_photo_file_id,
    get_category,
    get_product_with_photos,
    list_active_categories,
    list_products,
)

router = Router()

CATALOG_HEADER = "<b>Каталог решений</b>\nВыберите направление:"


@router.message(F.text == CATALOG_BTN)
async def show_catalog_from_menu(message: Message, session: AsyncSession):
    categories = await list_active_categories(session)
    if not categories:
        await message.answer("Каталог пока пуст.")
        return
    await message.answer(CATALOG_HEADER, reply_markup=categories_kb(categories))


@router.callback_query(F.data == "catalog")
async def show_catalog_callback(call: CallbackQuery, session: AsyncSession):
    categories = await list_active_categories(session)
    try:
        await call.message.edit_text(CATALOG_HEADER, reply_markup=categories_kb(categories))
    except TelegramBadRequest:
        await call.message.answer(CATALOG_HEADER, reply_markup=categories_kb(categories))
    await call.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_category(call: CallbackQuery, session: AsyncSession):
    category_id = int(call.data.split(":", 1)[1])
    category = await get_category(session, category_id)
    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return
    products = await list_products(session, category_id)
    if products:
        text = f"<b>{category.title}</b>\nВыберите модель:"
    else:
        text = f"<b>{category.title}</b>\n\nСкоро добавим проекты по этому направлению."
    try:
        await call.message.edit_text(text, reply_markup=products_kb(category_id, products))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=products_kb(category_id, products))
    await call.answer()


def _product_caption(product: Product) -> str:
    lines = [f"<b>{product.title}</b>"]
    if product.category:
        lines.append(f"Категория: {product.category.title}")
    if product.area_m2:
        lines.append(f"Площадь: {int(product.area_m2)} м²")
    if product.price:
        price_str = f"{int(product.price):,}".replace(",", " ")
        lines.append(f"Цена: {price_str} ₽")
    elif product.price_note:
        lines.append(f"Цена: {product.price_note}")
    else:
        lines.append("Цена: по запросу")
    if product.description:
        lines.append("")
        lines.append(product.description)
    return "\n".join(lines)


@router.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery, session: AsyncSession):
    product_id = int(call.data.split(":", 1)[1])
    product = await get_product_with_photos(session, product_id)
    if not product:
        await call.answer("Карточка не найдена", show_alert=True)
        return

    caption = _product_caption(product)
    photos = sorted(product.photos, key=lambda p: (not p.is_cover, p.sort_order, p.id))[:10]
    kb = product_card_kb(product.id, product.category_id)

    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass

    if not photos:
        await call.message.answer(caption, reply_markup=kb)
    elif len(photos) == 1:
        p = photos[0]
        photo = p.file_id or FSInputFile(p.local_path)
        sent = await call.message.answer_photo(photo, caption=caption, reply_markup=kb)
        if not p.file_id and sent.photo:
            await cache_photo_file_id(session, p.id, sent.photo[-1].file_id)
    else:
        media: list[InputMediaPhoto] = []
        for i, p in enumerate(photos):
            src = p.file_id or FSInputFile(p.local_path)
            media.append(
                InputMediaPhoto(
                    media=src,
                    caption=caption if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
            )
        sent_msgs = await call.message.answer_media_group(media)
        for i, msg in enumerate(sent_msgs):
            if i < len(photos) and not photos[i].file_id and msg.photo:
                await cache_photo_file_id(session, photos[i].id, msg.photo[-1].file_id)
        await call.message.answer("Действия:", reply_markup=kb)

    await call.answer()
