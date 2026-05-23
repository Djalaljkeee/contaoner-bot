from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import ContainerSpec, Product, ProductType
from bot.keyboards.catalog import (
    product_card_kb,
    products_kb,
    spec_filter_kb,
    type_kb,
)
from bot.keyboards.main import CATALOG_BTN
from bot.services.catalog import (
    cache_photo_file_id,
    get_product_with_photos,
    list_products,
)

router = Router()

_CATALOG_HEADER = "<b>Каталог проектов</b>\nВыберите тип:"

_TYPE_LABEL = {
    ProductType.house: "🏠 Дома",
    ProductType.office: "🏢 Офисы",
}

_SPEC_LABEL = {
    ContainerSpec.ft20: "20ft (14 м²)",
    ContainerSpec.ft40: "40ft (28 м²)",
    ContainerSpec.x2ft40: "2×40ft (56 м²)",
    ContainerSpec.x3ft40: "3×40ft (84 м²)",
}


async def _available_specs(session: AsyncSession, product_type: ProductType) -> list[ContainerSpec]:
    products = await list_products(session, product_type)
    seen: list[ContainerSpec] = []
    for p in products:
        if p.container_spec not in seen:
            seen.append(p.container_spec)
    return seen


@router.message(F.text == CATALOG_BTN)
async def show_catalog(message: Message):
    await message.answer(_CATALOG_HEADER, reply_markup=type_kb())


@router.callback_query(F.data == "catalog")
async def show_catalog_cb(call: CallbackQuery):
    try:
        await call.message.edit_text(_CATALOG_HEADER, reply_markup=type_kb())
    except TelegramBadRequest:
        await call.message.answer(_CATALOG_HEADER, reply_markup=type_kb())
    await call.answer()


@router.callback_query(F.data.startswith("ctype:"))
async def show_type(call: CallbackQuery, session: AsyncSession):
    type_str = call.data.split(":", 1)[1]
    try:
        product_type = ProductType(type_str)
    except ValueError:
        await call.answer("Неизвестный тип", show_alert=True)
        return

    specs = await _available_specs(session, product_type)
    type_name = _TYPE_LABEL.get(product_type, type_str)
    text = f"<b>{type_name}</b>\nВыберите размер контейнера:"
    kb = spec_filter_kb(type_str, specs)
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("cspec:"))
async def show_products_list(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    type_str = parts[1]
    spec_str = parts[2]

    try:
        product_type = ProductType(type_str)
    except ValueError:
        await call.answer("Неизвестный тип", show_alert=True)
        return

    spec: ContainerSpec | None = None
    if spec_str != "all":
        try:
            spec = ContainerSpec(spec_str)
        except ValueError:
            await call.answer("Неизвестный размер", show_alert=True)
            return

    products = await list_products(session, product_type, spec)
    type_name = _TYPE_LABEL.get(product_type, type_str)
    spec_name = _SPEC_LABEL.get(spec, spec_str) if spec else "все размеры"
    text = f"<b>{type_name} · {spec_name}</b>\nВыберите проект:"
    if not products:
        text = f"<b>{type_name} · {spec_name}</b>\n\nПроектов пока нет — скоро добавим."

    kb = products_kb(type_str, products, spec_str)
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()


def _product_caption(product: Product) -> str:
    from bot.db.models import BadgeType

    badge_map = {BadgeType.hit: "🔥 Хит", BadgeType.new: "🆕 Новинка", BadgeType.premium: "⭐ Премиум"}
    spec_map = {
        ContainerSpec.ft20: "20ft",
        ContainerSpec.ft40: "40ft",
        ContainerSpec.x2ft40: "2×40ft",
        ContainerSpec.x3ft40: "3×40ft",
    }

    lines = [f"<b>{product.title}</b>"]
    if product.badge:
        lines.append(badge_map.get(product.badge, ""))
    if product.area_m2:
        lines.append(f"Площадь: {int(product.area_m2)} м²")
    lines.append(f"Контейнер: {spec_map.get(product.container_spec, product.container_spec.value)}")
    if product.build_days:
        lines.append(f"Срок сборки: {product.build_days} дней")
    if product.price_from:
        price_str = f"{int(product.price_from):,}".replace(",", " ")
        lines.append(f"Цена от: {price_str} ₽")
    else:
        lines.append("Цена: по запросу")
    if product.description:
        lines.append("")
        lines.append(product.description)
    return "\n".join(lines)


@router.callback_query(F.data.startswith("cprod:"))
async def show_product(call: CallbackQuery, session: AsyncSession):
    product_id = int(call.data.split(":", 1)[1])
    product = await get_product_with_photos(session, product_id)
    if not product:
        await call.answer("Карточка не найдена", show_alert=True)
        return

    caption = _product_caption(product)
    photos = sorted(product.photos, key=lambda p: (not p.is_cover, p.sort_order, p.id))[:10]
    kb = product_card_kb(product.id, product.type.value)

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
        await call.message.answer("Выберите действие:", reply_markup=kb)

    await call.answer()
