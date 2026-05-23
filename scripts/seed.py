"""
Засев данных для konteiner24.ru: продукты, опции калькулятора, города доставки.
Идемпотентно — повторный запуск ничего не сломает.
"""
import asyncio
from decimal import Decimal

from sqlalchemy import select

from bot.db.base import SessionLocal, engine
from bot.db.models import (
    Base,
    BadgeType,
    CalcOption,
    CalcOptionGroup,
    ContainerSpec,
    DeliveryCity,
    Product,
    ProductType,
)

# (group, title, price_delta, area_m2, sort_order)
CALC_OPTIONS: list[tuple[str, str, int, int | None, int]] = [
    # modules
    ("module",     "20ft — 14 м²",                      790_000, 14, 10),
    ("module",     "40ft — 28 м²",                    1_850_000, 28, 20),
    ("module",     "2×40ft — 56 м² (два этажа)",      3_450_000, 56, 30),
    # insulation
    ("insulation", "Стандарт 50 мм",                          0, None, 10),
    ("insulation", "Усиленная 100 мм",                  120_000, None, 20),
    ("insulation", "Премиум 150 мм с пароизоляцией",    250_000, None, 30),
    # foundation
    ("foundation", "Бетонные блоки",                     90_000, None, 10),
    ("foundation", "Винтовые сваи",                     180_000, None, 20),
    ("foundation", "Монолитная плита",                  350_000, None, 30),
    # interior
    ("interior",   "Черновая отделка",                        0, None, 10),
    ("interior",   "Чистовая отделка",                  280_000, None, 20),
    ("interior",   "Под ключ",                           650_000, None, 30),
    # windows
    ("windows",    "Без окон",                                0, None, 10),
    ("windows",    "Энергосберегающие",                  150_000, None, 20),
    ("windows",    "Панорамные",                         450_000, None, 30),
]

# (name, distance_km, sort_order)
DELIVERY_CITIES: list[tuple[str, int, int]] = [
    ("Самовывоз (Москва, ул. Котляковская, 6)",    0,     0),
    ("Тверь",                                     170,   10),
    ("Тула",                                      180,   11),
    ("Калуга",                                    190,   12),
    ("Рязань",                                    195,   13),
    ("Владимир",                                  190,   14),
    ("Ярославль",                                 260,   15),
    ("Иваново",                                   300,   16),
    ("Нижний Новгород",                           410,   20),
    ("Воронеж",                                   500,   30),
    ("Санкт-Петербург",                           710,   40),
    ("Казань",                                    820,   50),
    ("Самара",                                  1_050,   60),
    ("Ростов-на-Дону",                          1_070,   70),
    ("Краснодар",                               1_340,   80),
    ("Уфа",                                     1_340,   90),
    ("Екатеринбург",                            1_780,  100),
    ("Новосибирск",                             3_300,  110),
]

# (type, container_spec, title, area_m2, price_from, build_days, badge, description, sort_order)
PRODUCTS: list[tuple[str, str, str, int, int, int, str | None, str, int]] = [
    (
        "house", "40ft", "Модерн Блэк 40ft",
        28, 1_850_000, 45, "hit",
        "Современный минималистичный дом с чёрным фасадом. "
        "28 м² жилого пространства из 40-футового контейнера.",
        10,
    ),
    (
        "house", "40ft", "Резиденция Серо 40ft",
        28, 2_100_000, 60, "new",
        "Просторный дом с панорамным остеклением и отделкой в серо-бетонном стиле.",
        20,
    ),
    (
        "house", "2x40ft", "Дуплекс Рустик 40ft×2",
        56, 3_450_000, 75, "premium",
        "Двухэтажный дом из двух 40-футовых контейнеров. "
        "56 м² с рустикальной отделкой из натурального дерева.",
        30,
    ),
    (
        "house", "20ft", "Коттедж Бриз 20ft",
        14, 790_000, 30, None,
        "Компактный загородный дом из 20-футового контейнера. "
        "Идеален как дача или гостевой дом.",
        40,
    ),
    (
        "office", "20ft", "Офис Нордик 20ft",
        14, 980_000, 25, None,
        "Мобильный офис из 20-футового контейнера в скандинавском стиле. "
        "Быстрый монтаж, готов к работе за 25 дней.",
        10,
    ),
    (
        "office", "3x40ft", "Офис-комплекс Эко 40ft×3",
        84, 5_200_000, 90, None,
        "Офисный комплекс из трёх 40-футовых контейнеров. "
        "84 м² с open-space зонированием и эко-отделкой.",
        20,
    ),
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        # --- calc_options ---
        existing_opts = set(
            (r.group.value, r.title)
            for r in (await session.execute(select(CalcOption))).scalars().all()
        )
        for group_str, title, price_delta, area_m2, sort_order in CALC_OPTIONS:
            if (group_str, title) in existing_opts:
                continue
            session.add(
                CalcOption(
                    group=CalcOptionGroup(group_str),
                    title=title,
                    price_delta=Decimal(str(price_delta)),
                    area_m2=Decimal(str(area_m2)) if area_m2 is not None else None,
                    sort_order=sort_order,
                    is_active=True,
                )
            )
        await session.commit()

        # --- delivery_cities ---
        existing_cities = set(
            r.name
            for r in (await session.execute(select(DeliveryCity))).scalars().all()
        )
        for name, distance_km, sort_order in DELIVERY_CITIES:
            if name in existing_cities:
                continue
            session.add(DeliveryCity(name=name, distance_km=distance_km, sort_order=sort_order))
        await session.commit()

        # --- products ---
        existing_products = set(
            r.title
            for r in (await session.execute(select(Product))).scalars().all()
        )
        for (
            type_str, spec_str, title, area_m2, price_from, build_days, badge_str, desc, sort_order
        ) in PRODUCTS:
            if title in existing_products:
                continue
            session.add(
                Product(
                    type=ProductType(type_str),
                    container_spec=ContainerSpec(spec_str),
                    title=title,
                    area_m2=Decimal(str(area_m2)),
                    price_from=Decimal(str(price_from)),
                    build_days=build_days,
                    badge=BadgeType(badge_str) if badge_str else None,
                    description=desc,
                    sort_order=sort_order,
                    is_active=True,
                )
            )
        await session.commit()

    print("Seed done.")


if __name__ == "__main__":
    asyncio.run(seed())
