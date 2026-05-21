"""
Засев каталога: 7 категорий + 8 моделей Skandy House с локальными фото.
Идемпотентно — повторный запуск ничего не сломает.
"""
import asyncio
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from bot.db.base import SessionLocal, engine
from bot.db.models import Base, Category, Product, ProductKind, ProductPhoto

PHOTO_DIR = Path(__file__).resolve().parent.parent / "data" / "photos"

CATEGORIES: list[tuple[str, str, int]] = [
    ("residential", "🏠 Жилые дома", 10),
    ("guest",       "🛏 Гостевые дома", 20),
    ("offices",     "🏢 Офисы и шоурумы", 30),
    ("cafes",       "🍔 Кафе и киоски", 40),
    ("shops",       "🛍 Магазины", 50),
    ("sheds",       "🧰 Сараи и склады", 60),
    ("misc",        "🧱 Разное (бани, бассейны, авто, спец.)", 70),
]

# (category_slug, model_name, area_m2, photo_file, sort_order, source_url)
SKANDY_MODELS: list[tuple[str, str, int, str, int, str]] = [
    ("residential", "Кама",   15, "15-Kama.png",   10, "https://из-контейнеров.рф/проект-кама-15м-²-дом-из-морского-кон/"),
    ("residential", "Обь",    30, "30-Ob.png",     20, "https://из-контейнеров.рф/проект-обь-30м-²-дом-из-морского-конт/"),
    ("residential", "Волга",  30, "30-Volga.png",  21, "https://из-контейнеров.рф/проект-волга-30м-²-дом-из-морского-ко/"),
    ("residential", "Ока",    30, "30-Oka.jpg",    22, "https://из-контейнеров.рф/проект-ока-30м-²-дом-из-морского-конт/"),
    ("residential", "Иртыш",  45, "45-Irtish.png", 30, "https://из-контейнеров.рф/проект-иртыш-45м-²-дом-из-морского-ко/"),
    ("residential", "Лена",   45, "45-2Lena.png",  31, "https://из-контейнеров.рф/проект-лена-45м-²-дом-из-морского-кон/"),
    ("residential", "Енисей", 60, "60-Enisei.png", 40, "https://из-контейнеров.рф/проект-енисей-60м-²-дом-из-морского-к/"),
    ("residential", "Амур",   90, "90-Amur.png",   50, "https://из-контейнеров.рф/проект-амур-90м-²-дом-из-морского-кон/"),
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        existing_cats = {
            c.slug: c
            for c in (await session.execute(select(Category))).scalars().all()
        }
        for slug, title, order in CATEGORIES:
            if slug in existing_cats:
                continue
            session.add(Category(slug=slug, title=title, sort_order=order, is_active=True))
        await session.commit()

        cat_map = {
            c.slug: c
            for c in (await session.execute(select(Category))).scalars().all()
        }

        for cat_slug, name, area, photo_name, order, source_url in SKANDY_MODELS:
            cat = cat_map[cat_slug]
            title = f"Проект «{name}»"
            existing = (
                await session.execute(
                    select(Product).where(
                        Product.category_id == cat.id,
                        Product.title == title,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                continue
            product = Product(
                category_id=cat.id,
                kind=ProductKind.model,
                title=title,
                area_m2=Decimal(str(area)),
                price_note="по запросу",
                source_url=source_url,
                sort_order=order,
                is_active=True,
            )
            session.add(product)
            await session.flush()

            photo_path = PHOTO_DIR / photo_name
            if photo_path.exists():
                session.add(
                    ProductPhoto(
                        product_id=product.id,
                        local_path=str(photo_path),
                        is_cover=True,
                        sort_order=0,
                    )
                )
            else:
                print(f"WARN: photo missing for {name}: {photo_path}")

        await session.commit()

    print("Seed done.")


if __name__ == "__main__":
    asyncio.run(seed())
