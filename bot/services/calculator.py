from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import CalcOption, CalcOptionGroup, DeliveryCity

DELIVERY_RATE = 55  # ₽/km


async def get_calc_options(
    session: AsyncSession, group: CalcOptionGroup
) -> list[CalcOption]:
    result = await session.execute(
        select(CalcOption)
        .where(CalcOption.group == group, CalcOption.is_active.is_(True))
        .order_by(CalcOption.sort_order, CalcOption.id)
    )
    return list(result.scalars().all())


async def list_delivery_cities(session: AsyncSession) -> list[DeliveryCity]:
    result = await session.execute(
        select(DeliveryCity).order_by(DeliveryCity.sort_order, DeliveryCity.id)
    )
    return list(result.scalars().all())


def fmt(amount: int | Decimal) -> str:
    return f"{int(amount):,}".replace(",", " ")


def calc_delivery(km: int) -> int:
    return km * DELIVERY_RATE


def build_summary(data: dict) -> str:
    module_price = int(data.get("module_price", 0))
    ins_delta = int(data.get("ins_price_delta", 0))
    fnd_delta = int(data.get("fnd_price_delta", 0))
    int_delta = int(data.get("int_price_delta", 0))
    win_delta = int(data.get("win_price_delta", 0))
    delivery_cost = int(data.get("delivery_cost", 0))

    subtotal_base = module_price
    subtotal_options = ins_delta + fnd_delta
    subtotal_finish = int_delta + win_delta
    total = subtotal_base + subtotal_options + subtotal_finish + delivery_cost

    city_label = data.get("delivery_city", "—")
    km = data.get("delivery_km", 0)
    delivery_label = f"{city_label} ({km} км)" if km else city_label

    lines = [
        "🧮 <b>Предварительный расчёт стоимости</b>",
        "",
        f"📦 Модуль: {data.get('module_title', '—')}",
        f"    <code>{fmt(module_price)} ₽</code>",
        f"🌡 Утепление: {data.get('ins_title', '—')}",
        f"    <code>+{fmt(ins_delta)} ₽</code>" if ins_delta else "    включено",
        f"🏗 Фундамент: {data.get('fnd_title', '—')}",
        f"    <code>+{fmt(fnd_delta)} ₽</code>",
        f"🛋 Интерьер: {data.get('int_title', '—')}",
        f"    <code>+{fmt(int_delta)} ₽</code>" if int_delta else "    включено",
        f"🪟 Окна: {data.get('win_title', '—')}",
        f"    <code>+{fmt(win_delta)} ₽</code>" if win_delta else "    не выбраны",
        f"🚚 Доставка: {delivery_label}",
        f"    <code>+{fmt(delivery_cost)} ₽</code>" if delivery_cost else "    самовывоз",
        "",
        "━━━━━━━━━━━━━━━━━",
        f"💰 <b>ИТОГО: {fmt(total)} ₽</b>",
        "",
        "<i>Цены ориентировочные. Точную стоимость уточнит менеджер.</i>",
    ]
    return "\n".join(lines)


def extract_calc_config(data: dict) -> dict:
    km = data.get("delivery_km", 0)
    delivery_cost = int(data.get("delivery_cost", 0))
    total = (
        int(data.get("module_price", 0))
        + int(data.get("ins_price_delta", 0))
        + int(data.get("fnd_price_delta", 0))
        + int(data.get("int_price_delta", 0))
        + int(data.get("win_price_delta", 0))
        + delivery_cost
    )
    return {
        "module": {
            "id": data.get("module_id"),
            "title": data.get("module_title"),
            "price": int(data.get("module_price", 0)),
            "area_m2": data.get("module_area_m2"),
        },
        "insulation": {
            "id": data.get("ins_id"),
            "title": data.get("ins_title"),
            "price_delta": int(data.get("ins_price_delta", 0)),
        },
        "foundation": {
            "id": data.get("fnd_id"),
            "title": data.get("fnd_title"),
            "price_delta": int(data.get("fnd_price_delta", 0)),
        },
        "interior": {
            "id": data.get("int_id"),
            "title": data.get("int_title"),
            "price_delta": int(data.get("int_price_delta", 0)),
        },
        "windows": {
            "id": data.get("win_id"),
            "title": data.get("win_title"),
            "price_delta": int(data.get("win_price_delta", 0)),
        },
        "delivery": {
            "city": data.get("delivery_city"),
            "km": km,
            "cost": delivery_cost,
        },
        "total": total,
    }
