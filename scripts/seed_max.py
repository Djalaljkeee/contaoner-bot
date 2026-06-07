"""
Засев данных Петрикс-Хоум: продукты, опции калькулятора.
Идемпотентно — повторный запуск ничего не сломает.
"""
import asyncio
import logging
import sys
import os

# Allow running as: python -m scripts.seed_max
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect as sa_inspect, select

from bot_max.db.base import SessionLocal, engine
from bot_max.db.models import (
    MaxBase,
    MaxCalcExtra,
    MaxCalcFinishingOption,
    MaxCalcInsulationOption,
    MaxCalcSizeOption,
    MaxProduct,
)

log = logging.getLogger(__name__)

# ─── Products ─────────────────────────────────────────────────────────────────
# (title, size_ft, price_from, badge, description, sort_order)
PRODUCTS = [
    (
        "Офис продаж 6×2.4 м",
        "20ft",
        215_000,
        "hit",
        "Компактный офис продаж из 20-футового контейнера. "
        "Быстрый монтаж, готов к эксплуатации за 2 недели.",
        10,
    ),
    (
        "Жилой модуль 12×2.4 м (Глэмпинг)",
        "40ft",
        360_000,
        "premium",
        "Просторный жилой модуль для глэмпинга из 40-футового контейнера. "
        "Панорамные окна, терраса, полная отделка.",
        20,
    ),
    (
        "Модульный дом с открытой террасой",
        "40ft",
        285_000,
        None,
        "Загородный дом с просторной открытой террасой. "
        "Идеально для дачи или гостевого домика.",
        30,
    ),
    (
        "Жилой модуль-студия 6×2.4 м",
        "20ft",
        168_000,
        "hit",
        "Компактная студия из 20-футового контейнера. "
        "Оптимальное решение для дачи или временного жилья.",
        40,
    ),
    (
        "Премиум модуль с панорамным фасадом",
        "20ft",
        320_000,
        None,
        "Стильный модуль премиум-класса с панорамным остеклением. "
        "Современный дизайн, качественная отделка.",
        50,
    ),
    (
        "Лесной модуль с крытой верандой",
        "20ft",
        245_000,
        None,
        "Уютный модуль для лесного отдыха с крытой верандой. "
        "Идеален для эко-туризма и глэмпинга.",
        60,
    ),
]

# ─── Calculator size options ──────────────────────────────────────────────────
# (title, base_price)
SIZE_OPTIONS = [
    ("20ft (6×2.4 м)", 168_000),
    ("40ft (12×2.4 м)", 285_000),
]

# ─── Calculator insulation options ────────────────────────────────────────────
# (title, price_delta)
INSULATION_OPTIONS = [
    ("100 мм", 0),
    ("150 мм", 25_000),
    ("200 мм", 55_000),
]

# ─── Calculator finishing options ─────────────────────────────────────────────
# (title, price_delta)
FINISHING_OPTIONS = [
    ("Эконом", 0),
    ("Стандарт", 40_000),
    ("Премиум", 90_000),
]

# ─── Calculator extras ────────────────────────────────────────────────────────
# (title, price_delta, sort_order)
EXTRAS = [
    ("Электрика под ключ", 45_000, 10),
    ("Санузел с душем", 85_000, 20),
    ("Терраса", 60_000, 30),
    ("Кондиционер", 35_000, 40),
]


def _ensure_schema_max(sync_conn) -> None:
    """Drop old max_ schema if columns don't match, then create."""
    inspector = sa_inspect(sync_conn)
    if inspector.has_table("max_leads"):
        cols = {c["name"] for c in inspector.get_columns("max_leads")}
        if "product_title" not in cols or "user_id" not in cols:
            log.warning("Outdated max_ schema — dropping all max_ tables and recreating")
            MaxBase.metadata.drop_all(sync_conn)
    MaxBase.metadata.create_all(sync_conn)


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(_ensure_schema_max)

    async with SessionLocal() as session:
        # ── products ──────────────────────────────────────────────────────────
        existing_products = {
            r.title
            for r in (await session.execute(select(MaxProduct))).scalars().all()
        }
        for title, size_ft, price_from, badge, description, sort_order in PRODUCTS:
            if title not in existing_products:
                session.add(
                    MaxProduct(
                        title=title,
                        size_ft=size_ft,
                        price_from=price_from,
                        badge=badge,
                        description=description,
                        sort_order=sort_order,
                        is_active=True,
                    )
                )
        await session.commit()

        # ── size options ──────────────────────────────────────────────────────
        existing_sizes = {
            r.title
            for r in (await session.execute(select(MaxCalcSizeOption))).scalars().all()
        }
        for title, base_price in SIZE_OPTIONS:
            if title not in existing_sizes:
                session.add(MaxCalcSizeOption(title=title, base_price=base_price))
        await session.commit()

        # ── insulation options ────────────────────────────────────────────────
        existing_ins = {
            r.title
            for r in (await session.execute(select(MaxCalcInsulationOption))).scalars().all()
        }
        for title, price_delta in INSULATION_OPTIONS:
            if title not in existing_ins:
                session.add(MaxCalcInsulationOption(title=title, price_delta=price_delta))
        await session.commit()

        # ── finishing options ─────────────────────────────────────────────────
        existing_fin = {
            r.title
            for r in (await session.execute(select(MaxCalcFinishingOption))).scalars().all()
        }
        for title, price_delta in FINISHING_OPTIONS:
            if title not in existing_fin:
                session.add(MaxCalcFinishingOption(title=title, price_delta=price_delta))
        await session.commit()

        # ── extras ────────────────────────────────────────────────────────────
        existing_extras = {
            r.title
            for r in (await session.execute(select(MaxCalcExtra))).scalars().all()
        }
        for title, price_delta, sort_order in EXTRAS:
            if title not in existing_extras:
                session.add(
                    MaxCalcExtra(title=title, price_delta=price_delta, sort_order=sort_order)
                )
        await session.commit()

    print("MAX seed done.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())
