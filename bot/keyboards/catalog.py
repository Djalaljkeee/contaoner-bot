from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.db.models import BadgeType, ContainerSpec, Product, ProductType

_BADGE_LABEL = {
    BadgeType.hit: " 🔥",
    BadgeType.new: " 🆕",
    BadgeType.premium: " ⭐",
}

_SPEC_LABEL = {
    ContainerSpec.ft20: "20ft",
    ContainerSpec.ft40: "40ft",
    ContainerSpec.x2ft40: "2×40ft",
    ContainerSpec.x3ft40: "3×40ft",
}


def type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏠 Дома", callback_data="ctype:house"),
                InlineKeyboardButton(text="🏢 Офисы", callback_data="ctype:office"),
            ]
        ]
    )


def spec_filter_kb(product_type: str, specs: list[ContainerSpec]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for spec in specs:
        btn = InlineKeyboardButton(
            text=_SPEC_LABEL.get(spec, spec.value),
            callback_data=f"cspec:{product_type}:{spec.value}",
        )
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if len(specs) > 1:
        rows.append(
            [InlineKeyboardButton(text="Все размеры", callback_data=f"cspec:{product_type}:all")]
        )
    rows.append([InlineKeyboardButton(text="« Назад", callback_data="catalog")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def products_kb(product_type: str, products: list[Product], spec_filter: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for p in products:
        badge = _BADGE_LABEL.get(p.badge, "") if p.badge else ""
        area = f" · {int(p.area_m2)} м²" if p.area_m2 else ""
        price = f" · от {int(p.price_from):,} ₽".replace(",", " ") if p.price_from else ""
        label = f"{p.title}{badge}{area}{price}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"cprod:{p.id}")])
    rows.append(
        [InlineKeyboardButton(text="« К фильтру", callback_data=f"ctype:{product_type}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_card_kb(product_id: int, product_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉ Заказать этот проект",
                    callback_data=f"lead_start:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="« К списку",
                    callback_data=f"ctype:{product_type}",
                )
            ],
        ]
    )
