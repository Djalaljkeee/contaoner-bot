from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.db.models import (
    MaxCalcExtra,
    MaxCalcFinishingOption,
    MaxCalcInsulationOption,
    MaxCalcSizeOption,
)


def fmt(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


async def get_size_options(session: AsyncSession) -> list[MaxCalcSizeOption]:
    result = await session.execute(select(MaxCalcSizeOption).order_by(MaxCalcSizeOption.id))
    return list(result.scalars().all())


async def get_insulation_options(session: AsyncSession) -> list[MaxCalcInsulationOption]:
    result = await session.execute(
        select(MaxCalcInsulationOption).order_by(MaxCalcInsulationOption.id)
    )
    return list(result.scalars().all())


async def get_finishing_options(session: AsyncSession) -> list[MaxCalcFinishingOption]:
    result = await session.execute(
        select(MaxCalcFinishingOption).order_by(MaxCalcFinishingOption.id)
    )
    return list(result.scalars().all())


async def get_extras(session: AsyncSession) -> list[MaxCalcExtra]:
    result = await session.execute(
        select(MaxCalcExtra).order_by(MaxCalcExtra.sort_order, MaxCalcExtra.id)
    )
    return list(result.scalars().all())


def build_summary(data: dict) -> str:
    base_price = int(data.get("size_base_price", 0))
    insulation_delta = int(data.get("insulation_delta", 0))
    finishing_delta = int(data.get("finishing_delta", 0))
    extras_delta = int(data.get("extras_delta", 0))
    total = base_price + insulation_delta + finishing_delta + extras_delta

    selected_extras_titles: list[str] = data.get("selected_extras_titles", [])

    lines = [
        "🧮 Предварительный расчёт стоимости",
        "",
        f"📦 Размер модуля: {data.get('size_title', '—')}",
        f"    {fmt(base_price)} ₽",
        f"🌡 Утепление: {data.get('insulation_title', '—')}",
    ]
    if insulation_delta:
        lines.append(f"    +{fmt(insulation_delta)} ₽")
    else:
        lines.append("    включено")

    lines.append(f"🛋 Отделка: {data.get('finishing_title', '—')}")
    if finishing_delta:
        lines.append(f"    +{fmt(finishing_delta)} ₽")
    else:
        lines.append("    включено")

    if selected_extras_titles:
        lines.append("⚙️ Дополнительно:")
        for title in selected_extras_titles:
            lines.append(f"    • {title}")
        lines.append(f"    +{fmt(extras_delta)} ₽")

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━",
        f"💰 ИТОГО: {fmt(total)} ₽",
        "",
        "Цены ориентировочные. Точную стоимость уточнит менеджер.",
    ]
    return "\n".join(lines)


def extract_config(data: dict) -> dict[str, Any]:
    base_price = int(data.get("size_base_price", 0))
    insulation_delta = int(data.get("insulation_delta", 0))
    finishing_delta = int(data.get("finishing_delta", 0))
    extras_delta = int(data.get("extras_delta", 0))
    total = base_price + insulation_delta + finishing_delta + extras_delta
    return {
        "size": {
            "id": data.get("size_id"),
            "title": data.get("size_title"),
            "base_price": base_price,
        },
        "insulation": {
            "id": data.get("insulation_id"),
            "title": data.get("insulation_title"),
            "price_delta": insulation_delta,
        },
        "finishing": {
            "id": data.get("finishing_id"),
            "title": data.get("finishing_title"),
            "price_delta": finishing_delta,
        },
        "extras": data.get("selected_extras_ids", []),
        "extras_titles": data.get("selected_extras_titles", []),
        "extras_delta": extras_delta,
        "total": total,
    }
